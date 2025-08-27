import os
import argparse
from rdflib import Graph
from tabulate import tabulate
import matplotlib.pyplot as plt
from collections import defaultdict

def load_graphs(base_dir):
    """
    Walk through the base_dir and load all JSON-LD files into rdflib Graphs.
    """
    graph_list = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".jsonld"):
                file_path = os.path.join(root, file)
                try:
                    g = Graph()
                    g.parse(file_path, format='json-ld')
                    graph_list.append(g)
                    print(f"✅ Parsed: {file_path}")
                except Exception as e:
                    print(f"❌ Failed to parse {file_path}: {e}")
    print(f"\nTotal graphs loaded: {len(graph_list)}")
    return graph_list


def query_and_build_table(graph_list):
    """
    Run SPARQL query on graphs and build a table.
    Returns headers and table_data.
    """
    query = """
    PREFIX cr: <http://mlcommons.org/croissant/>
    PREFIX sio: <http://semanticscience.org/resource/>

    SELECT DISTINCT ?tool_name ?value_element_size ?value_young_modulus ?value_poisson_ratio ?value_max_mises_stress
    WHERE {
      ?max_mises_stress cr:source/cr:extract [ cr:jsonPath "/max_mises_stress" ] ;
                 sio:SIO_000210 [ schema:value ?value_max_mises_stress ] ;
            cr:source/schema:MediaObject ?media_object_max_mises_stress .

      ?processing_step schema:result ?media_object_max_mises_stress ;
            schema:object ?media_object_element_size .

      ?poisson_ratio cr:source/cr:extract [ cr:jsonPath "/poisson-ratio/value" ] ;
                 sio:SIO_000210 [ schema:value ?value_poisson_ratio ] .

      ?young_modulus cr:source/cr:extract [ cr:jsonPath "/young-modulus/value" ] ;
                 sio:SIO_000210 [ schema:value ?value_young_modulus ] .

      ?field_size cr:source/cr:extract [ cr:jsonPath "/element-size/value" ] ;
                 sio:SIO_000210 [ schema:value ?value_element_size ] ;
            cr:source/schema:MediaObject ?media_object_element_size . 

      ?tool a schema:SoftwareApplication ;
            rdfs:label ?tool_name .

      FILTER EXISTS {
        ?field_degree cr:source/cr:extract [ cr:jsonPath "/element-degree" ] ;
                      sio:SIO_000210 [ schema:value 1 ] ;
            cr:source/schema:MediaObject ?media_object_element_size .          
      }

      FILTER EXISTS {
        ?field_order cr:source/cr:extract [ cr:jsonPath "/element-order" ] ;
                     sio:SIO_000210 [ schema:value 1 ] ;
            cr:source/schema:MediaObject ?media_object_element_size .         
      }
    }
    """

    headers = [
        "Simulation Hash",
        "Tool Name",
        "element-size",
        "young-modulus",
        "poisson-ratio",
        "max-mises-stress"
    ]

    table_data = []

    for g in graph_list:
        local_ns = dict(g.namespace_manager.namespaces()).get("local")
        hash_id = local_ns.strip("/").split("/")[-1] if local_ns else "UNKNOWN"

        results = g.query(query)

        for row in results:
            table_data.append([
                hash_id,
                row.tool_name,
                row.value_element_size,
                row.value_young_modulus,
                row.value_poisson_ratio,
                row.value_max_mises_stress
            ])

    # Sort by element-size
    sort_key = headers.index("element-size")
    table_data.sort(key=lambda x: x[sort_key])

    return headers, table_data


def print_table(headers, table_data):
    """Prints the table using tabulate."""
    print(tabulate(table_data, headers=headers, tablefmt="grid"))


def plot_element_size_vs_stress(headers, table_data, output_file="element_size_vs_stress.pdf"):
    """Plots element-size vs max-mises-stress grouped by tool and saves as PDF."""
    idx_element_size = headers.index("element-size")
    idx_stress = headers.index("max-mises-stress")
    idx_tool = headers.index("Tool Name")

    grouped_data = defaultdict(list)
    x_tick_set = set()

    for row in table_data:
        tool = row[idx_tool]
        x = float(row[idx_element_size])
        y = float(row[idx_stress])
        grouped_data[tool].append((x, y))
        x_tick_set.add(x)

    x_ticks = sorted(x_tick_set)

    plt.figure(figsize=(12, 5))
    for tool, values in grouped_data.items():
        values.sort()
        x_vals, y_vals = zip(*values)
        plt.plot(x_vals, y_vals, marker='o', linestyle='-', label=tool)

    plt.xlabel("element-size")
    plt.ylabel("max-mises-stress")
    plt.title("element-size vs max-mises-stress by Tool")
    plt.legend(title="Tool Name")
    plt.grid(True)
    plt.xticks(ticks=x_ticks, labels=[str(x) for x in x_ticks], rotation=45)
    plt.tight_layout()
    
    # Save to PDF instead of showing
    plt.savefig(output_file)
    print(f"Plot saved as {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process JSON-LD artifacts and display simulation results.")
    parser.add_argument("artifact_folder", type=str, help="Path to the folder containing unzipped artifacts")
    args = parser.parse_args()

    graphs = load_graphs(args.artifact_folder)
    headers, table_data = query_and_build_table(graphs)
    plot_element_size_vs_stress(headers, table_data, output_file="element_size_vs_stress.pdf")

