import argparse
from provenance import ProvenanceAnalyzer
from generate_config import workflow_config
import json
import os
import pandas as pd


def parse_args():
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
        default="ro-crate-metadata.json",
        help="File name for the provenance graph",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        required=True,
        help="Final visualization file",
    )
    return parser.parse_args()


def sparql_result_to_dataframe(results):
    """
    Convert SPARQL results (rdflib.query.Result) into a pandas DataFrame.
    Uses row.asdict() to dynamically extract bindings.
    """
    rows = []

    for row in results:
        row_dict = {k: v.toPython() for k, v in row.asdict().items()}
        rows.append(row_dict)

    return pd.DataFrame(rows)


def apply_custom_filters(data: pd.DataFrame) -> pd.DataFrame:
    """
    Filter rows in a pandas DataFrame and return a list of lists
    with element_size, max_von_mises_stress_nodes, and tool_name.
    """

    filtered_df = data[(data["element_degree"] == 1) & (data["element_order"] == 1)]

    return filtered_df[
        ["element_size", "max_von_mises_stress_nodes", "tool_name"]
    ].reset_index(drop=True)


def summary_file_to_dataframe(summary_path, parameters, metrics):
    """
    Load JSON benchmark data into a DataFrame.
    Automatically detects whether parameter values are dicts (with 'value')
    or direct scalar values.
    """
    with open(summary_path, "r") as f:
        data = json.load(f)

    records = []
    for entry in data:
        record = {}

        for p in parameters:
            json_name = p.replace("_", "-")
            param_value = entry["parameters"][json_name]

            if isinstance(param_value, dict):
                record[p] = param_value.get("value")
            else:
                record[p] = param_value

        for m in metrics:
            metric_value = entry["metrics"][m]

            if isinstance(metric_value, dict):
                record[m] = metric_value.get("value")
            else:
                record[m] = metric_value

        records.append(record)

    return pd.DataFrame(records)


def compare_dataframes(df1: pd.DataFrame, df2: pd.DataFrame):
    """
    Compare two DataFrames for identical values (regardless of row order)
    and print which rows do not match.

    Returns True if DataFrames are identical, False otherwise.
    """
    # Sort columns and rows to make comparison order-independent
    cols1 = sorted(df1.columns)
    cols2 = sorted(df2.columns)

    if cols1 != cols2:
        raise ValueError("DataFrames have different columns.")

    df1_sorted = df1[cols1].sort_values(by=cols1).reset_index(drop=True)
    df2_sorted = df2[cols2].sort_values(by=cols2).reset_index(drop=True)

    # Check equality
    are_equal = df1_sorted.equals(df2_sorted)

    if are_equal:
        return True

    # Find rows in df1 but not in df2
    missing_in_df2 = pd.concat([df1_sorted, df2_sorted, df2_sorted]).drop_duplicates(
        keep=False
    )

    # Find rows in df2 but not in df1
    missing_in_df1 = pd.concat([df2_sorted, df1_sorted, df1_sorted]).drop_duplicates(
        keep=False
    )

    print("Rows in df1 but not in df2:")
    print(missing_in_df2 if not missing_in_df2.empty else "None")

    print("\nRows in df2 but not in df1:")
    print(missing_in_df1 if not missing_in_df1.empty else "None")

    return False


def main():
    args = parse_args()

    parameters = ["element_size", "element_order", "element_degree"]
    metrics = ["max_von_mises_stress_nodes"]
    tools = workflow_config["tools"]

    analyzer = ProvenanceAnalyzer(
        provenance_folderpath=args.provenance_folderpath,
        provenance_filename=args.provenance_filename,
    )

    graph = analyzer.load_graph_from_file()
    query = analyzer.build_dynamic_query(parameters, metrics, tools)
    results = analyzer.run_query_on_graph(graph, query)

    provenance_df = sparql_result_to_dataframe(results)

    assert len(provenance_df), "No data found for the provenance query."

    for tool in tools:
        summary_path = os.path.join(
            args.provenance_folderpath,
            "snakemake_results",
            "linear-elastic-plate-with-hole",
            tool,
            "summary.json",
        )
        summary_df = summary_file_to_dataframe(summary_path, parameters, metrics)
        filtered_data_df = provenance_df[
            provenance_df["tool_name"].str.contains(tool, case=False, na=False)
        ]
        filtered_data_df = filtered_data_df.drop(columns=["tool_name"])
        assert compare_dataframes(
            summary_df, filtered_data_df
        ), f"Data mismatch for tool '{tool}'. See above for details."

    final_df = apply_custom_filters(provenance_df)

    analyzer.plot_provenance_graph(
        data=final_df.values.tolist(),
        x_axis_label="Element Size",
        y_axis_label="Max Von Mises Stress",
        x_axis_index=0,
        y_axis_index=1,
        group_by_index=2,
        title="Element Size vs Max Von Mises Stress ",
        output_file=args.output_file,
    )


if __name__ == "__main__":
    main()
