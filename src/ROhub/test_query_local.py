from rdflib import Graph, URIRef, Namespace

# Load RO-Crate metadata
graph = Graph()
graph.parse("ro-crate-metadata.json", format="json-ld")

# Define namespaces
SCHEMA = Namespace("http://schema.org/")

try:
    # Show datasets and their dct:conformsTo values
    debug_query = """
    PREFIX schema: <http://schema.org/>
    PREFIX dct: <http://purl.org/dc/terms/>
    SELECT ?dataset ?ct WHERE {
        ?dataset a schema:Dataset .
        OPTIONAL { ?dataset dct:conformsTo ?ct }
    }
    """
    print("DEBUG: All datasets and their dct:conformsTo objects")
    print("=" * 60)
    for row in graph.query(debug_query):
        print(f"Dataset: {row.dataset}")
        print(f"ConformsTo: {row.ct if row.ct else 'None'}")
        print("-" * 40)

    # Find datasets that conform to Workflow RO-Crate 1.0
    query = """
        PREFIX schema: <http://schema.org/>
        PREFIX dct: <http://purl.org/dc/terms/>
        SELECT ?dataset ?datePublished ?author ?part WHERE {
            ?dataset a schema:Dataset .
            ?dataset dct:conformsTo <https://w3id.org/workflowhub/workflow-ro-crate/1.0> .
            ?dataset schema:author ?author .
            FILTER (?author = <https://orcid.org/0000-0000-0000-0000>)
            OPTIONAL { ?dataset schema:datePublished ?datePublished }
            OPTIONAL { ?dataset schema:hasPart ?part }
        }
    """
    results = graph.query(query)

    print("\nWorkflowHub Dataset Query Results:")
    print("========================================")
    # Print directly per row instead of aggregating into a structure
    found_any = False
    for row in results:
        found_any = True
        print(f"Dataset: {row.dataset}")
        print(f"Date Published: {row.datePublished if row.datePublished else 'None'}")
        print(f"Author: {row.author if row.author else 'None'}")
        print(f"Part: {row.part if row.part else 'None'}")
        print("-" * 40)

    if not found_any:
        print("No datasets found that conform to Workflow RO-Crate 1.0")

except Exception as e:
    print(f"Error: {e}")
