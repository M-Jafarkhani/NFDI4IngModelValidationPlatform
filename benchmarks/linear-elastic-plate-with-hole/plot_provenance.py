import os
import argparse
from rdflib import Graph
import matplotlib.pyplot as plt
from collections import defaultdict
from generate_config import workflow_config
import json

COL_TOOL_NAME = "Tool Name"

PARAM_ELEMENT_SIZE = "element-size"
PARAM_ELEMENT_ORDER = "element-order"
PARAM_ELEMENT_DEGREE = "element-degree"

METRIC_MAX_MISES_NODES = "max_von_mises_stress_nodes"

BENCHMARK_NAME = "linear-elastic-plate-with-hole"
SUMMARY_FILENAME = "summary.json"
SNAKEMAKE_RESULTS_FOLDER = "snakemake_results"


def load_graphs(base_dir):
    """
    Walk through the base_dir and load all JSON-LD files into rdflib Graphs.
    """
    graph_list = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file == "provenance.jsonld":
                file_path = os.path.join(root, file)
                try:
                    g = Graph()
                    g.parse(file_path, format="json-ld")
                    graph_list.append(g)
                except Exception as e:
                    print(f"Failed to parse {file_path}: {e}")
    print(f"\nTotal graphs loaded: {len(graph_list)}")
    return graph_list


def query_and_build_table(graph_list):
    """
    Run SPARQL query on graphs and build a table.
    Returns headers and table_data.
    """
    tools = workflow_config["tools"]
    filter_conditions = " || ".join(
        f'CONTAINS(LCASE(?tool_name), "{tool.lower()}")' for tool in tools
    )
    query = f"""
    SELECT DISTINCT ?value_element_size ?value_max_von_mises_stress_gauss_points ?tool_name
    WHERE {{
      ?method a m4i:Method ;
            m4i:hasParameter ?element_size ;
            m4i:hasParameter ?element_order ;
            m4i:hasParameter ?element_degree ;
            m4i:investigates ?max_von_mises_stress_gauss_points ;
            ssn:implementedBy ?tool .
    
      ?max_von_mises_stress_gauss_points a schema:PropertyValue ;
            rdfs:label "max_von_mises_stress_nodes" ;
            schema:value ?value_max_von_mises_stress_gauss_points .
            
      ?element_order a schema:PropertyValue ;
            rdfs:label "element_order" ;
            schema:value 1 .

      ?element_degree a schema:PropertyValue ;
            rdfs:label "element_degree" ;
            schema:value 1 .

      ?element_size a schema:PropertyValue ;
            rdfs:label "element_size" ;
            schema:value ?value_element_size .

      ?tool a schema:SoftwareApplication ;
            rdfs:label ?tool_name .
            
      FILTER ({filter_conditions})
    }}
    """

    headers = [PARAM_ELEMENT_SIZE, METRIC_MAX_MISES_NODES, COL_TOOL_NAME]

    table_data = []

    for g in graph_list:
        results = g.query(query)
        for row in results:
            value_element_size = row.value_element_size
            value_max_von_mises_stress_gauss_points = (
                row.value_max_von_mises_stress_gauss_points
            )
            tool_name = row.tool_name
            table_data.append(
                [
                    value_element_size,
                    value_max_von_mises_stress_gauss_points,
                    tool_name,
                ]
            )

    # Sort by element-size
    sort_key = headers.index(PARAM_ELEMENT_SIZE)
    table_data.sort(key=lambda x: x[sort_key])

    assert (
        len(table_data) > 0
    ), "No rows returned from SPARQL query — table_data is empty."

    return headers, table_data


def plot_element_size_vs_stress(headers, table_data, output_file):
    """Plots element-size vs max-mises-stress grouped by tool and saves as PDF."""

    idx_element_size = headers.index(PARAM_ELEMENT_SIZE)
    idx_stress = headers.index(METRIC_MAX_MISES_NODES)
    idx_tool = headers.index(COL_TOOL_NAME)

    grouped_data = defaultdict(list)
    x_tick_set = set()

    for row in table_data:
        tool = row[idx_tool]
        x = float(row[idx_element_size])
        y = float(row[idx_stress])
        grouped_data[tool].append((x, y))
        x_tick_set.add(x)

    # Sort x-tick labels
    x_ticks = sorted(x_tick_set)

    plt.figure(figsize=(12, 5))
    for tool, values in grouped_data.items():
        values.sort()
        x_vals, y_vals = zip(*values)
        plt.plot(x_vals, y_vals, marker="o", linestyle="-", label=tool)

    plt.xlabel(PARAM_ELEMENT_SIZE)
    plt.ylabel(METRIC_MAX_MISES_NODES)
    plt.title(
        f"{PARAM_ELEMENT_SIZE} vs {METRIC_MAX_MISES_NODES} by Tool\n(element-order = 1 , element-degree = 1)"
    )
    plt.legend(title=COL_TOOL_NAME)
    plt.grid(True)

    # Use logarithmic scale for x-axis
    plt.xscale("log")

    # Set x-ticks to show original values
    plt.xticks(ticks=x_ticks, labels=[str(x) for x in x_ticks], rotation=45)
    plt.tight_layout()

    # Save to file
    plt.savefig(output_file)


def load_truth_from_summary(base_dir, tools, benchmark):
    """
    Read summary.json for each tool and extract truth data:
        (tool, element_size) → max_von_mises_stress_nodes
    """
    truth = {}

    for tool in tools:
        summary_path = os.path.join(
            base_dir,
            SNAKEMAKE_RESULTS_FOLDER,
            benchmark,
            tool,
            SUMMARY_FILENAME,
        )

        if not os.path.exists(summary_path):
            raise FileNotFoundError(
                f"Expected {SNAKEMAKE_RESULTS_FOLDER} for tool '{tool}' at: {summary_path}"
            )

        with open(summary_path, "r") as f:
            entries = json.load(f)

        for entry in entries:
            p = entry["parameters"]
            m = entry["metrics"]

            # Only include entries matching the SPARQL query filter
            if p["element-order"] != 1 or p["element-degree"] != 1:
                continue

            element_size = float(p["element-size"]["value"])
            stress_nodes = float(m["max_von_mises_stress_nodes"])

            truth[(tool, element_size)] = stress_nodes

    if not truth:
        raise ValueError(f"No matching entries found in {SUMMARY_FILENAME}")

    return truth


def extract_sparql_rows(headers, table_data, tools):
    """
    Convert SPARQL table_data into:
        (normalized_tool, element_size) → stress
    using simple substring matching between tool names.
    """
    idx_size = headers.index(PARAM_ELEMENT_SIZE)
    idx_stress = headers.index(METRIC_MAX_MISES_NODES)
    idx_tool = headers.index(COL_TOOL_NAME)

    extracted = {}

    for row in table_data:
        raw_tool = str(row[idx_tool]).strip().lower()
        element_size = float(row[idx_size])
        stress = float(row[idx_stress])

        # Substring match for tool name
        matched_tool = None
        for t in tools:
            if t in raw_tool:
                matched_tool = t
                break

        if matched_tool is None:
            raise AssertionError(
                f"No matching tool for SPARQL tool name '{raw_tool}'. "
                f"Expected one of {tools} to be contained in the name."
            )

        extracted[(matched_tool, element_size)] = stress

    return extracted


def compare_truth_and_extracted(truth, extracted):
    """
    Compare truth table vs SPARQL extracted table.
    """
    if set(truth.keys()) != set(extracted.keys()):
        missing = set(truth.keys()) - set(extracted.keys())
        extra = set(extracted.keys()) - set(truth.keys())
        raise AssertionError(
            f"Mismatch in provenance keys:\n"
            f"Missing in SPARQL: {missing}\n"
            f"Extra in SPARQL: {extra}"
        )

    # numerical comparison
    for key in truth:
        expected = truth[key]
        got = extracted[key]
        if abs(expected - got) > 1e-6:
            tool, esize = key
            raise AssertionError(
                f"Mismatch provenance extraction for tool='{tool}', {PARAM_ELEMENT_SIZE}={esize}:\n"
                f"Expected={expected} but Extracted={got}"
            )


def ensure_provenance_data(base_dir, headers, table_data) -> bool:
    """
    Main orchestrator: validate provenance by comparing summary.json data
    against SPARQL output.
    """
    tools = [t.lower() for t in workflow_config["tools"]]
    benchmark = BENCHMARK_NAME

    truth = load_truth_from_summary(base_dir, tools, benchmark)
    extracted = extract_sparql_rows(headers, table_data, tools)
    compare_truth_and_extracted(truth, extracted)

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process JSON-LD artifacts and display simulation results."
    )
    parser.add_argument(
        "--artifact_folder",
        type=str,
        required=True,
        help="Path to the folder containing unzipped artifacts",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        required=True,
        help="File name with extension for the final file to visualize the graph",
    )
    args = parser.parse_args()

    graphs = load_graphs(args.artifact_folder)
    headers, table_data = query_and_build_table(graphs)
    
    assert ensure_provenance_data(args.artifact_folder, headers, table_data)
    
    plot_element_size_vs_stress(
        headers,
        table_data,
        output_file=args.output_file,
    )
