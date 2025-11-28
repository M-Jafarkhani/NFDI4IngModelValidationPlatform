import os
import json
from rdflib import Graph
import matplotlib.pyplot as plt
from collections import defaultdict
from typing import List, Tuple, Dict
import re


class ProvenanceAnalyzer:
    """
    A class to analyze and visualize provenance data from a JSON-LD file,
    typically adhering to the RO-Crate standard.

    It uses SPARQL queries to extract specific workflow metadata (element size,
    tool name, max von Mises stress) and performs validation against a known
    "ground truth" found in summary.json files. Finally, it visualizes the
    extracted data.

    Attributes:
        provenance_folderpath (str): The directory path containing the provenance file.
        provenance_filename (str): The name of the provenance file (default: 'ro-crate-metadata.json').
        tools (List[str]): A list of tool names (substrings) to filter the provenance data.
        headers (List[str]): Headers of the table data extracted from the SPARQL query.
        table_data (List[List]): The data extracted from the SPARQL query results.
    """

    # Constants
    COL_TOOL_NAME = "Tool Name"
    PARAM_ELEMENT_SIZE = "element-size"
    PARAM_ELEMENT_ORDER = "element-order"
    PARAM_ELEMENT_DEGREE = "element-degree"
    METRIC_MAX_MISES_NODES = "max_von_mises_stress_nodes"
    SUMMARY_FILENAME = "summary.json"
    SNAKEMAKE_RESULTS_FOLDER = "snakemake_results"
    BENCHMARK_NAME = "linear-elastic-plate-with-hole"

    def __init__(
        self,
        tools: List[str],
        provenance_folderpath: str = None,
        provenance_filename: str = "ro-crate-metadata.json",
    ):
        """
        Initialize the ProvenanceAnalyzer.

        Args:
            tools (List[str]): A list of tool name substrings (e.g., ["kratos", "fenics"])
                               used for filtering the provenance data.
            provenance_folderpath (str, optional): Path to the folder containing the provenance file.
                                                   Defaults to None.
            provenance_filename (str, optional): Name of the provenance file.
                                                 Defaults to "ro-crate-metadata.json".
        """
        self.provenance_folderpath = provenance_folderpath
        self.provenance_filename = provenance_filename
        self.tools = tools

    def load_graph_from_file(self) -> Graph:
        """
        Loads the provenance file (`ro-crate-metadata.json`) into an `rdflib` Graph object.

        Returns:
            rdflib.Graph: The loaded RDF graph.

        Raises:
            Exception: If the file cannot be parsed as JSON-LD.
        """
        try:
            g = Graph()
            # The parse method handles file loading and format parsing
            g.parse(
                os.path.join(self.provenance_folderpath, self.provenance_filename),
                format="json-ld",
            )
            return g
        except Exception as e:
            print(f"Failed to parse {self.provenance_filename}: {e}")
            raise  # Re-raise to ensure error is handled

    def generate_query_string(self, named_graph: str = None) -> str:
        """
        Generates the SPARQL query string used to extract specific provenance data.

        It targets the element size and max von Mises stress at nodes for workflows
        where element order and element degree are 1. The query includes a filter
        to match the specified tools.

        Args:
            named_graph (str, optional): An optional URI for querying a specific named graph.
                                         Defaults to None (queries the default graph).

        Returns:
            str: The complete SPARQL query string.
        """
        # Build the SPARQL filter for tool names
        filter_conditions = " || ".join(
            f'CONTAINS(LCASE(?tool_name), "{tool.lower()}")' for tool in self.tools
        )

        # Literal "1" handling based on whether a named graph is used
        literal_1 = "1" if named_graph is None else '"1"'

        PREFIXES = f"""
        PREFIX schema: <http://schema.org/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX m4i: <http://w3id.org/nfdi4ing/metadata4ing#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX ssn: <http://www.w3.org/ns/ssn/>
        """

        SELECT_ELEMETS = (
            f"?value_element_size ?value_max_von_mises_stress_gauss_points ?tool_name"
        )

        # Inner part of the query defining the required graph pattern
        INNER_QUERY = f"""
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
                schema:value {literal_1} .
    
          ?element_degree a schema:PropertyValue ;
                rdfs:label "element_degree" ;
                schema:value {literal_1} .
    
          ?element_size a schema:PropertyValue ;
                rdfs:label "element_size" ;
                schema:value ?value_element_size .
    
          ?tool a schema:SoftwareApplication ;
                rdfs:label ?tool_name .
        """

        QUERY_STR = ""

        if named_graph is None:
            # Query the default graph
            QUERY_STR = f"""
            {PREFIXES}
            SELECT DISTINCT { SELECT_ELEMETS}
            WHERE {{
              { INNER_QUERY }
              FILTER ({filter_conditions})
            }}
            """
        else:
            # Query a specific named graph
            QUERY_STR = f"""
            {PREFIXES}
            SELECT DISTINCT { SELECT_ELEMETS}
            WHERE {{
                GRAPH <{named_graph}> {{
                    { INNER_QUERY }
                    FILTER ({filter_conditions})
                }}
            }}
            """

        return QUERY_STR

    def sanitize_variable_name(self, name: str) -> str:
        """
        Convert a string into a valid SPARQL variable name.
        Replaces invalid characters with underscores.
        """
        # Replace invalid chars with underscore
        var = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        # Ensure it doesn't start with a digit
        if re.match(r"^\d", var):
            var = "_" + var
        return var

    def build_dynamic_query(self, parameters, metrics, tools=None, named_graph=None):
        """
        Generate a SPARQL query for all m4i:Method instances with given parameters and metrics.
        Parameters and metrics are mandatory; optional filtering by tool names.
        Optionally, the query can target a specific named graph.
        """

        all_names = parameters + metrics
        # Map original names to safe SPARQL variable names
        var_map = {name: self.sanitize_variable_name(name) for name in all_names}

        # Build SELECT variables
        select_vars = " ".join(f"?value_{var_map[name]}" for name in all_names)

        # Build method→parameter and method→metric links
        method_links = (
            "\n    ".join(
                f"?method m4i:hasParameter ?{var_map[p]} ." for p in parameters
            )
            + "\n"
            + "\n    ".join(
                f"?method m4i:investigates ?{var_map[m]} ." for m in metrics
            )
        )

        # Build parameter and metric blocks
        value_blocks = "\n".join(
            f'?{var_map[name]} a schema:PropertyValue ;\n rdfs:label "{name}" ;\n schema:value ?value_{var_map[name]} .\n'
            for name in all_names
        )

        # Tool block with optional filter
        tool_block = "?method ssn:implementedBy ?tool .\n?tool a schema:SoftwareApplication ;\n rdfs:label ?tool_name .\n"
        if tools:
            filter_cond = " || ".join(
                f'CONTAINS(LCASE(?tool_name), "{t.lower()}")' for t in tools
            )
            tool_block += f"\nFILTER({filter_cond}) .\n"

        # Build the inner query
        inner_query = f"""
        ?method a m4i:Method .
        {method_links}
        {value_blocks}
        {tool_block}
        """.strip()

        # Wrap in GRAPH if named_graph is provided
        where_block = (
            f"GRAPH <{named_graph}> {{\n{inner_query}\n}}"
            if named_graph
            else inner_query
        )

        # Final query
        query = f"""
        PREFIX schema: <http://schema.org/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX m4i: <http://w3id.org/nfdi4ing/metadata4ing#>
        PREFIX ssn: <http://www.w3.org/ns/ssn/>
    
        SELECT ?method {select_vars} ?tool_name
        WHERE {{
            {where_block}
        }}
        """.strip()

        return query

    def run_query_on_graph(
        self, graph: Graph, query: str
    ) -> Tuple[List[str], List[List]]:
        """
        Executes the SPARQL query on the provided RDF graph and formats the results into a table.

        Args:
            graph (rdflib.Graph): The RDF graph to query.
            query (str): The SPARQL query string to execute.

        Returns:
            Tuple[List[str], List[List]]: A tuple containing the table headers and the sorted table data.

        Raises:
            AssertionError: If the query returns no rows.
        """
        return graph.query(query)

    def plot_provenance_graph(
        self,
        data: List[List],
        x_axis_label: str,
        y_axis_label: str,
        x_axis_index: str,
        y_axis_index: str,
        group_by_index: str,
        title: str,
        output_file: str = None,
        figsize: Tuple[int, int] = (12, 5),
    ):
        """
        Generates a scatter/line plot of the extracted data.

        Args:
            output_file (str, optional): Path where the PDF plot will be saved. If None, the plot is shown.
            headers (List[str], optional): Table headers to use.
            table_data (List[List], optional): Table data to use.
            figsize (Tuple[int, int], optional): Dimensions of the output figure. Defaults to (12, 5).
        """

        grouped_data = defaultdict(list)
        x_tick_set = set()

        for row in data:
            x = float(row[x_axis_index])
            y = float(row[y_axis_index])
            grouped_data[row[group_by_index]].append((x, y))
            x_tick_set.add(x)

        # Sort x-tick labels
        x_ticks = sorted(x_tick_set)

        plt.figure(figsize=figsize)
        for grouped_title, values in grouped_data.items():
            # Sort values by x-axis (element size) to ensure correct line plotting
            values.sort()
            x_vals, y_vals = zip(*values)
            plt.plot(x_vals, y_vals, marker="o", linestyle="-", label=grouped_title)

        plt.xlabel(x_axis_label)
        plt.ylabel(y_axis_label)
        plt.title(title)
        plt.grid(True)

        # Use logarithmic scale for x-axis
        plt.xscale("log")

        # Set x-ticks to show original values
        plt.xticks(ticks=x_ticks, labels=[str(x) for x in x_ticks], rotation=45)
        plt.tight_layout()

        if output_file:
            plt.savefig(output_file)
            print(f"Plot saved to: {output_file}")
        else:
            plt.show()

    def load_truth_from_summary(self) -> Dict[Tuple[str, float], float]:
        """
        Reads the ground truth data from the `summary.json` files.

        It looks for summary files within the Snakemake results structure
        (/snakemake_results/benchmark_name/tool/summary.json) and filters for entries
        where `element-order` and `element-degree` are 1, matching the SPARQL query criteria.

        Returns:
            Dict[Tuple[str, float], float]: A dictionary mapping (tool_name, element_size)
                                            to the ground truth max_von_mises_stress_nodes.

        Raises:
            FileNotFoundError: If a required `summary.json` file is missing.
            ValueError: If no matching entries are found in the summaries.
        """
        truth = {}

        for tool in self.tools:
            summary_path = os.path.join(
                self.provenance_folderpath,
                self.SNAKEMAKE_RESULTS_FOLDER,
                self.BENCHMARK_NAME,
                tool,
                self.SUMMARY_FILENAME,
            )

            if not os.path.exists(summary_path):
                raise FileNotFoundError(
                    f"Expected {self.SUMMARY_FILENAME} for tool '{tool}' at: {summary_path}"
                )

            with open(summary_path, "r") as f:
                entries = json.load(f)

            for entry in entries:
                p = entry["parameters"]
                m = entry["metrics"]

                # Only include entries matching the SPARQL query filter
                # element-order and element-degree must be 1
                if (
                    p[self.PARAM_ELEMENT_ORDER] != 1
                    or p[self.PARAM_ELEMENT_DEGREE] != 1
                ):
                    continue

                element_size = float(p[self.PARAM_ELEMENT_SIZE]["value"])
                stress_nodes = float(m[self.METRIC_MAX_MISES_NODES])

                truth[(tool, element_size)] = stress_nodes

        if not truth:
            raise ValueError(
                f"No matching entries found in {self.SUMMARY_FILENAME} that satisfy the filter criteria."
            )

        return truth

    def extract_sparql_rows(
        self, headers: List[str], table_data: List[List]
    ) -> Dict[Tuple[str, float], float]:
        """
        Converts the raw SPARQL query results (`table_data`) into a normalized dictionary
        format for comparison. It normalizes tool names by performing a substring
        match against `self.tools`.

        Args:
            headers (List[str], optional): Optional headers list.
            table_data (List[List], optional): Optional table data.

        Returns:
            Dict[Tuple[str, float], float]: A dictionary mapping (normalized_tool, element_size)
                                            to the extracted stress value.

        Raises:
            AssertionError: If a tool name from SPARQL results doesn't match any tool in `self.tools`.
        """
        idx_size = headers.index(self.PARAM_ELEMENT_SIZE)
        idx_stress = headers.index(self.METRIC_MAX_MISES_NODES)
        idx_tool = headers.index(self.COL_TOOL_NAME)

        extracted = {}

        for row in table_data:
            # Convert raw tool name to lowercase string for robust matching
            raw_tool = str(row[idx_tool]).strip().lower()
            # Convert values to float for numerical key/comparison
            element_size = float(row[idx_size])
            stress = float(row[idx_stress])

            # Substring match to normalize the tool name
            matched_tool = None
            for t in self.tools:
                if t in raw_tool:
                    matched_tool = t
                    break

            if matched_tool is None:
                raise AssertionError(
                    f"No matching tool for SPARQL tool name '{raw_tool}'. "
                    f"Expected one of {self.tools} to be contained in the name."
                )

            extracted[(matched_tool, element_size)] = stress

        return extracted

    def compare_truth_and_extracted(self, truth: Dict, extracted: Dict):
        """
        Performs a validation check by comparing the ground truth data against the
        data extracted via SPARQL. It checks for key mismatches (missing or extra data points)
        and numerical value mismatches using a standard tolerance of $10^{-6}$.

        Args:
            truth (Dict): The ground truth dictionary.
            extracted (Dict): The SPARQL extracted data dictionary.

        Raises:
            AssertionError: If any mismatch in keys or values is detected.
        """
        # 1. Key comparison (ensure same data points exist in both sets)
        if set(truth.keys()) != set(extracted.keys()):
            missing = set(truth.keys()) - set(extracted.keys())
            extra = set(extracted.keys()) - set(truth.keys())
            raise AssertionError(
                f"Mismatch in provenance keys (data points):\n"
                f"Missing in SPARQL: {missing}\n"
                f"Extra in SPARQL: {extra}"
            )

        # 2. Numerical value comparison
        TOLERANCE = 1e-6
        for key in truth:
            expected = truth[key]
            got = extracted[key]
            # Check if the absolute difference exceeds the tolerance
            if abs(expected - got) > TOLERANCE:
                tool, esize = key
                raise AssertionError(
                    f"Mismatch provenance extraction for tool='{tool}', "
                    f"{self.PARAM_ELEMENT_SIZE}={esize}:\n"
                    f"Expected={expected} but Extracted={got} (Diff: {abs(expected - got):.8f})"
                )

    def validate_provenance(
        self, headers: List[str] = None, table_data: List[List] = None
    ) -> bool:
        """
        The main validation workflow. It loads the ground truth from summary.json,
        extracts the data from the SPARQL query results, and calls
        `compare_truth_and_extracted`.

        Returns:
            bool: True if validation passes without raising an exception.

        Raises:
            AssertionError: If validation fails (via `compare_truth_and_extracted`).
        """
        truth = self.load_truth_from_summary()
        extracted = self.extract_sparql_rows(headers, table_data)
        self.compare_truth_and_extracted(truth, extracted)

        return True

    def run_full_analysis(self, output_file: str):
        """
        Executes the complete analysis pipeline in order: load graph, run SPARQL query,
        validate provenance, and generate the final plot.

        Args:
            output_file (str): Path to save the output plot PDF.

        Returns:
            Tuple[List[str], List[List]]: The headers and table data.
        """
        print("Loading graphs...")

        graph = self.load_graph_from_file()

        query_str = self.generate_query_string()

        print("Querying and building table...")

        headers, table_data = self.run_query_on_graph(graph, query_str)

        print("Validating provenance...")
        self.validate_provenance(headers, table_data)

        print("Generating plot...")
        self.plot_element_size_vs_stress(output_file, headers, table_data)
