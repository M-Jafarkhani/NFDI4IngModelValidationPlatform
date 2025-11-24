import os
import json
from rdflib import Graph
import matplotlib.pyplot as plt
from collections import defaultdict
from typing import List, Tuple, Dict

class ProvenanceAnalyzer:
    """
    A class to analyze and visualize provenance data from JSON-LD files.
    
    Attributes:
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
    
    def __init__(self, tools: List[str], provenance_folderpath: str = None, provenance_filename: str = "ro-crate-metadata.json"):
        """
        Initialize the ProvenanceAnalyzer.
        
        Args:
        """
        self.provenance_folderpath = provenance_folderpath
        self.provenance_filename = provenance_filename
        self.tools = tools
        self.graphs = []
        self.headers = []
        self.table_data = []
        
    def load_graph_from_file(self) -> Graph:
        """
        
        Returns:
            List of loaded rdflib Graph objects
        """
        try:
            g = Graph()
            g.parse(os.path.join(self.provenance_folderpath,self.provenance_filename), format="json-ld")
            return g
        except Exception as e:
            print(f"Failed to parse {self.provenance_filename}: {e}")
    
    def generate_query_string(self, named_graph: str = None) -> str:
        filter_conditions = " || ".join(
            f'CONTAINS(LCASE(?tool_name), "{tool.lower()}")' for tool in self.tools
        )
        
        literal_1 = "1" if named_graph is None else "\"1\""
        
        PREFIXES = f"""
        PREFIX schema: <http://schema.org/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX m4i: <http://w3id.org/nfdi4ing/metadata4ing#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX ssn: <http://www.w3.org/ns/ssn/>
        """
        
        SELECT_ELEMETS = f"?value_element_size ?value_max_von_mises_stress_gauss_points ?tool_name"
        
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
            QUERY_STR = f"""
            {PREFIXES}
            SELECT DISTINCT { SELECT_ELEMETS}
            WHERE {{
              { INNER_QUERY }
              FILTER ({filter_conditions})
            }}
            """
        else:
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
        
    def run_query_on_graph(self, graph: Graph, query: str) -> Tuple[List[str], List[List]]:
        """
        Run SPARQL query on graphs and build a table.
        
        Args:
            graph_list: Optional list of graphs to query. If None, uses self.graphs
            
        Returns:
            Tuple of (headers, table_data)
        """
            
        headers = [self.PARAM_ELEMENT_SIZE, self.METRIC_MAX_MISES_NODES, self.COL_TOOL_NAME]
        table_data = []
        
        results = graph.query(query)
        
        for row in results:
            value_element_size = row.value_element_size
            value_max_von_mises_stress_gauss_points = row.value_max_von_mises_stress_gauss_points
            tool_name = row.tool_name
            table_data.append([
                value_element_size,
                value_max_von_mises_stress_gauss_points,
                tool_name,
            ])
        
        # Sort by element-size
        sort_key = headers.index(self.PARAM_ELEMENT_SIZE)
        table_data.sort(key=lambda x: x[sort_key])
        
        assert len(table_data) > 0, "No rows returned from SPARQL query — table_data is empty."
        
        self.headers = headers
        self.table_data = table_data
        return headers, table_data
    
    def plot_element_size_vs_stress(self, output_file: str = None, headers: List[str] = None, 
                                    table_data: List[List] = None, figsize: Tuple[int, int] = (12, 5)):
        """
        Plot element-size vs max-mises-stress grouped by tool and save as PDF.
        
        Args:
            output_file: Path to save the plot
            headers: Optional headers list. If None, uses self.headers
            table_data: Optional table data. If None, uses self.table_data
            figsize: Figure size tuple (width, height)
        """
        if headers is None:
            headers = self.headers
        if table_data is None:
            table_data = self.table_data
            
        idx_element_size = headers.index(self.PARAM_ELEMENT_SIZE)
        idx_stress = headers.index(self.METRIC_MAX_MISES_NODES)
        idx_tool = headers.index(self.COL_TOOL_NAME)
        
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
        
        plt.figure(figsize=figsize)
        for tool, values in grouped_data.items():
            values.sort()
            x_vals, y_vals = zip(*values)
            plt.plot(x_vals, y_vals, marker="o", linestyle="-", label=tool)
        
        plt.xlabel(self.PARAM_ELEMENT_SIZE)
        plt.ylabel(self.METRIC_MAX_MISES_NODES)
        plt.title(
            f"{self.PARAM_ELEMENT_SIZE} vs {self.METRIC_MAX_MISES_NODES} by Tool\n"
            f"(element-order = 1 , element-degree = 1)"
        )
        plt.legend(title=self.COL_TOOL_NAME)
        plt.grid(True)
        
        # Use logarithmic scale for x-axis
        plt.xscale("log")
        
        # Set x-ticks to show original values
        plt.xticks(ticks=x_ticks, labels=[str(x) for x in x_ticks], rotation=45)
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file)
        else:
            plt.show()
                
        print(f"Plot saved to: {output_file}")
    
    def load_truth_from_summary(self) -> Dict[Tuple[str, float], float]:
        """
        Read summary.json for each tool and extract truth data.
        
        Returns:
            Dictionary mapping (tool, element_size) to max_von_mises_stress_nodes
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
                    f"Expected {self.SNAKEMAKE_RESULTS_FOLDER} for tool '{tool}' at: {summary_path}"
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
            raise ValueError(f"No matching entries found in {self.SUMMARY_FILENAME}")
        
        return truth
    
    def extract_sparql_rows(self, headers: List[str] = None, 
                           table_data: List[List] = None) -> Dict[Tuple[str, float], float]:
        """
        Convert SPARQL table_data into normalized format.
        
        Args:
            headers: Optional headers list. If None, uses self.headers
            table_data: Optional table data. If None, uses self.table_data
            
        Returns:
            Dictionary mapping (normalized_tool, element_size) to stress
        """
        if headers is None:
            headers = self.headers
        if table_data is None:
            table_data = self.table_data
            
        idx_size = headers.index(self.PARAM_ELEMENT_SIZE)
        idx_stress = headers.index(self.METRIC_MAX_MISES_NODES)
        idx_tool = headers.index(self.COL_TOOL_NAME)
        
        extracted = {}
        
        for row in table_data:
            raw_tool = str(row[idx_tool]).strip().lower()
            element_size = float(row[idx_size])
            stress = float(row[idx_stress])
            
            # Substring match for tool name
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
        Compare truth table vs SPARQL extracted table.
        
        Args:
            truth: Ground truth dictionary
            extracted: Extracted data dictionary
            
        Raises:
            AssertionError: If there are mismatches in keys or values
        """
        if set(truth.keys()) != set(extracted.keys()):
            missing = set(truth.keys()) - set(extracted.keys())
            extra = set(extracted.keys()) - set(truth.keys())
            raise AssertionError(
                f"Mismatch in provenance keys:\n"
                f"Missing in SPARQL: {missing}\n"
                f"Extra in SPARQL: {extra}"
            )
        
        # Numerical comparison
        for key in truth:
            expected = truth[key]
            got = extracted[key]
            if abs(expected - got) > 1e-6:
                tool, esize = key
                raise AssertionError(
                    f"Mismatch provenance extraction for tool='{tool}', "
                    f"{self.PARAM_ELEMENT_SIZE}={esize}:\n"
                    f"Expected={expected} but Extracted={got}"
                )
    
    def validate_provenance(self) -> bool:
        """
        Main validation method: compare summary.json data against SPARQL output.
        
        Returns:
            True if validation passes
            
        Raises:
            AssertionError: If validation fails
        """
        truth = self.load_truth_from_summary()
        extracted = self.extract_sparql_rows()
        self.compare_truth_and_extracted(truth, extracted)
        
        return True
    
    def run_full_analysis(self, output_file: str):
        """
        Run the complete analysis pipeline: load, query, validate, and plot.
        
        Args:
            output_file: Path to save the output plot
            
        Returns:
            Tuple of (headers, table_data)
        """
        print("Loading graphs...")
        
        g = self.load_graph_from_file()
        
        query_str = self.generate_query_string()
        
        print("Querying and building table...")
        _, _ = self.run_query_on_graph(graph=g, query=query_str)
        
        print("Validating provenance...")
        self.validate_provenance()
        
        print("Generating plot...")
        self.plot_element_size_vs_stress(output_file)
