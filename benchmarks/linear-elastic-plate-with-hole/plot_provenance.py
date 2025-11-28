import argparse
from provenance import ProvenanceAnalyzer
from generate_config import workflow_config

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process ro-crate-metadata.json artifacts and display simulation results."
    )
    parser.add_argument(
        "--provenance_folderpath",
        type=str,
        required=True,
        help="Path to the folder containing provenance data",
    )
    parser.add_argument(
        "--provenance_filename",
        type=str,
        required=False,
        default="ro-crate-metadata.json",
        help="File name for the provenance graph",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        required=True,
        help="File name with extension for the final file to visualize the graph",
    )

    args = parser.parse_args()

    parameters = ["element_size", "element_order", "element_degree"]
    metrics = ["max_von_mises_stress_nodes"]
    tools = workflow_config["tools"]

    analyzer = ProvenanceAnalyzer(
        tools=tools,
        provenance_folderpath=args.provenance_folderpath,
        provenance_filename=args.provenance_filename,
    )

    graph = analyzer.load_graph_from_file()
    query_string = analyzer.build_dynamic_query(parameters, metrics, tools)
    results = analyzer.run_query_on_graph(graph, query_string)

    data = [
        [
            row["value_element_size"].toPython(),
            row["value_max_von_mises_stress_nodes"].toPython(),
            row["tool_name"].toPython(),
        ]
        for row in results
        if row["value_element_degree"].toPython() == 1
        and row["value_element_order"].toPython() == 1
    ]

    assert len(data) > 0, "No data found for the given query and filters."
    
    analyzer.plot_provenance_graph(
        data=data,
        x_axis_label="Element Size",
        y_axis_label="Max Von Mises Stress",
        x_axis_index=0,
        y_axis_index=1,
        group_by_index=2,
        title="Element Size vs Max Von Mises Stress ",
    )
