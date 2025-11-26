import argparse
from  provenance import ProvenanceAnalyzer
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
    
    tools = workflow_config["tools"]
    
    analyzer = ProvenanceAnalyzer(
        tools=tools,
        provenance_folderpath=args.provenance_folderpath,
        provenance_filename=args.provenance_filename,
    )
    
    analyzer.run_full_analysis(output_file=args.output_file)