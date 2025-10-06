from SPARQLWrapper import SPARQLWrapper, JSON

# SPARQL endpoint
sparql = SPARQLWrapper(
    "https://rohub2020-api-virtuoso-route-rohub.apps.paas-dev.psnc.pl/sparql/"
)

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

sparql.setQuery(query)
sparql.setReturnFormat(JSON)

try:
    resp = sparql.query().convert()
    bindings = resp.get("results", {}).get("bindings", [])

    print("Dataset Query Results:")
    print("========================================")
    # Print directly per row instead of aggregating into a structure
    for row in bindings:
        print(f"Dataset: {row.get('dataset', {}).get('value', 'None')}")
        print(f"Date Published: {row.get('datePublished', {}).get('value', 'None')}")
        print(f"Author: {row.get('author', {}).get('value', 'None')}")
        print(f"Part: {row.get('part', {}).get('value', 'None')}")
        print("-" * 40)

except Exception as e:
    print(f"Error executing SPARQL query: {e}")
