import os
from rdflib import Graph
import matplotlib.pyplot as plt
from collections import defaultdict
from typing import List, Tuple
import re
from rocrate_validator import services, models

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

    def __init__(
        self,
        provenance_folderpath: str = None,
        provenance_filename: str = "ro-crate-metadata.json",
    ):
        """
        Initialize the ProvenanceAnalyzer.

        Args:
            provenance_folderpath (str, optional): Path to the folder containing the provenance file.
                                                   Defaults to None.
            provenance_filename (str, optional): Name of the provenance file.
                                                 Defaults to "ro-crate-metadata.json".
        """
        self.provenance_folderpath = provenance_folderpath
        self.provenance_filename = provenance_filename

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
        select_vars = " ".join(f"?{var_map[name]}" for name in all_names)

        # Build method→parameter and method→metric links
        method_links = (
            "\n    ".join(
                f"?method m4i:hasParameter ?param_{var_map[p]} ." for p in parameters
            )
            + "\n"
            + "\n    ".join(
                f"?method m4i:investigates ?param_{var_map[m]} ." for m in metrics
            )
        )

        # Build parameter and metric blocks
        value_blocks = "\n".join(
            f'?param_{var_map[name]} a schema:PropertyValue ;\n rdfs:label "{name}" ;\n schema:value ?{var_map[name]} .\n'
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
    
        SELECT {select_vars} ?tool_name
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
        plt.legend()
        plt.xscale("log")

        # Set x-ticks to show original values
        plt.xticks(ticks=x_ticks, labels=[str(x) for x in x_ticks], rotation=45)
        plt.tight_layout()

        if output_file:
            plt.savefig(output_file)
            print(f"Plot saved to: {output_file}")
        else:
            plt.show()


    def validate_provevance(self): 
        settings = services.ValidationSettings(
            rocrate_uri=os.path.join(self.provenance_folderpath, self.provenance_filename),
            profile_identifier='ro-crate-1.1',
            requirement_severity=models.Severity.REQUIRED,
        )

        result = services.validate(settings)

        assert not result.has_issues(), (
            "RO-Crate is invalid!\n" +
            "\n".join(
                f"Detected issue of severity {issue.severity.name} with check "
                f'"{issue.check.identifier}": {issue.message}'
                for issue in result.get_issues()
            )
        )

        print("RO-Crate is valid!")