
# Using RoHub Python API

## Setup
To get started with RoHub using code, you can install [RoHub Python API](https://gitlab.pcss.pl/daisd-public/rohub/rohub-api). You can create a `yml` file, which will install the package into your current directory. 
```yml
name: rohub_dev
channels:
- conda-forge
dependencies:
- python=3.12
- sparqlwrapper
- pip
- pip:
- "--editable=git+https://gitlab.pcss.pl/daisd-public/rohub/rohub-api.git#egg=rohub"
```
You can also install from develop branch, which may contain some functions which are not still in the latest release:

```bash
--editable git+https://gitlab.pcss.pl/daisd-public/rohub/rohub-api.git@develop#egg=rohub
```

After creating an environment, you have to specify which RoHub endpoints you want to use. There are two endpoints: [Production](https://www.rohub.org/) and [Development](https://rohub2020-rohub.apps.paas-dev.psnc.pl/).  To work with the development endpoint , you have to find the location of the local installation (`pip show rohub`) and copy the file `.env` into this directory using a single command:
```bash
cp -v .env "$(pip show rohub | awk -F': ' '/Editable project location/ {print $2}')/.env"
```
This is a sample `.env` file which connects to the Development:

```bash
[API_SECTION]
API_URL = https://rohub2020-rohub.apps.paas-dev.psnc.pl/api/

[KEYCLOAK_SECTION]
KEYCLOAK_CLIENT_ID = rohub2020-cli
KEYCLOAK_CLIENT_SECRET = 714617a7-87bc-4a88-8682-5f9c2f60337d
KEYCLOAK_URL = https://keycloak-dev.apps.paas-dev.psnc.pl/auth/realms/rohub/protocol/openid-connect/token
```
Value for `API_URL` specifies the endpoint. For Development, it should be 
```bash
API_URL = https://rohub2020-rohub.apps.paas-dev.psnc.pl/api/
```
and for Production:
```bash
API_URL = https://api.rohub.org/api/
```
If you copy the `.env` file in the wrong location, it will automatically works with the Production endpoint.

## Login
Before start coding, you need to create an account. You need to create separate accounts for  [Production](https://www.rohub.org/) and [Development](https://rohub2020-rohub.apps.paas-dev.psnc.pl/).  After creating an account, you need your username and password to login into hub, and start working with research objects:

```python
import  rohub

print("ROHub API URL:", rohub.settings.API_URL)

user_name=  "your username"
user_pwd  =  "your password"

rohub.login(username=user_name, password=user_pwd)
```

Now you can list your uploaded research objects, and print their properties:

```python
my_ros  =  rohub.list_my_ros()

for  index, row  in  my_ros.iterrows():
	id  =  row["identifier"]
	ro  =  rohub.ros_load(id)
	print("RO type:", ro.ros_type)
	if  hasattr(ro, "title") and  ro.title:
		print("RO title:", ro.title)
	if  hasattr(ro, "authors") and  ro.authors:
		print("RO authors:", ro.authors)
	if  hasattr(ro, "description") and  ro.description:
		print("RO description:", ro.description)
	if  hasattr(ro, "research_areas") and  ro.research_areas:
		print("RO research areas:", ro.research_areas)
	if  hasattr(ro, "creation_date") and  ro.creation_date:
		print("RO creation date:", ro.creation_date)
	if  hasattr(ro, "last_modified_date") and  ro.last_modified_date:
		print("RO last modified date:", ro.last_modified_date)
	if  hasattr(ro, "doi") and  ro.doi:
		print("RO DOI:", ro.doi)
	if  hasattr(ro, "url") and  ro.url:
		print("RO URL:", ro.url)
	if  hasattr(ro, "metadata") and  ro.metadata:
		print("RO metadata:", ro.metadata)
```

## Uploading Research Objects
You can upload a research object like:

```python
import  rohub

research_areas  = ["Environmental research"]
title  =  "NFDI4ING Model Validation with NextFlow"
description  =  f"Description for {title}"
zip_path = "./ro-crate-metadata-21b6d1a7d9acc988.zip"
RO  =  rohub.ros_upload(path_to_zip=zip_path)
print(f"Identifier: {RO.identifier}")
```

After successfully uploading or creating a research object, api gives back its `identifier` which could be viewed on the portal. For example, if the identifier is `15b15e62-6136-4f04-a9eb-99c201befe0d`, then you can view it on https://w3id.org/ro-id-dev/15b15e62-6136-4f04-a9eb-99c201befe0d or https://w3id.org/ro-id/15b15e62-6136-4f04-a9eb-99c201befe0d, depending on which endpoint you are working on with. 

## Accessing Research Objects

You can access research objects via code (API) or SPARQL endpoint. There are two endpoints, [Production](https://rohub2020-api-virtuoso-route-rohub2020.apps.paas.psnc.pl/sparql) and [Development](https://rohub2020-api-virtuoso-route-rohub.apps.paas-dev.psnc.pl/sparql/%22).

You can query object properties by id as:

```sparql
SELECT *
WHERE {
  <https://w3id.org/ro-id-dev/15b15e62-6136-4f04-a9eb-99c201befe0d> ?p ?o .
}
```

## Adding Annotations
You can annotate a resource as well. For example, for a research object with identifier `e2cd6485-8400-4c49-91e1-feb2e9402596`  you can add a list of properties and values:

```python
RO  =  rohub.ros_load("e2cd6485-8400-4c49-91e1-feb2e9402596")
annotation_json  = [
	{
		"property": "http://hasStudySubject.com",
		"value": "http://inspire.ec.europa.eu/metadata-codelist/TopicCategory/environment"
	}
]
add_annotations_result = RO.add_annotations(body_specification_json=annotation_json)
```
After adding these annotations, it will appear in your SPARQL query:
```sparql
SELECT *
WHERE {
  <https://w3id.org/ro-id/e2cd6485-8400-4c49-91e1-feb2e9402596> <http://hasStudySubject.com> ?o .
}
```

## Access to `ro-crate-metadata.json` Contents

After uploading or creating a research object, you can access all the data in `ro-crate-metadata.json` as triples. To get started, let's assume we have a research object with identifier `c87448ad-5e9a-49fa-85e5-1fed9ecf9709`. The contents are in a named graph, but in order to find it, we have to query its Dataset:
```sparql
SELECT *
WHERE {
  GRAPH ?g {
    <https://w3id.org/ro-id-dev/c87448ad-5e9a-49fa-85e5-1fed9ecf9709> a <http://schema.org/Dataset> .
  }
}
```
This query should return a single value, which is the named graph for `ro-crate-metadata.json`. In our example, the named graph should be:
```
https://w3id.org/ro-id-dev/c87448ad-5e9a-49fa-85e5-1fed9ecf9709/.ro/annotations/c45c44b2-3afb-4059-9505-25fc03b60139.ttl
```
Now that we have found the named graph, we can query on it:
```sparql
SELECT *
WHERE {
  GRAPH <https://w3id.org/ro-id-dev/c87448ad-5e9a-49fa-85e5-1fed9ecf9709/.ro/annotations/c45c44b2-3afb-4059-9505-25fc03b60139.ttl> {
    ?s ?p ?o .
  }
}
```
This query returns the triples that are in the `ro-crate-metadata.json` file. For example, if the file contains a node as:
```json
{
    "@id": "#task/1cc8abe917eea617237b37eb263499f7",
    "@type": "CreateAction",
    "name": "summary (1)",
    "instrument": null,
    "agent": {
        "@id": "https://orcid.org/0000-0000-0000-0000"
    },
    "object": [
        {
            "@id": "file:///home/runner/work/NFDI4IngModelValidationPlatform/NFDI4IngModelValidationPlatform/benchmarks/linear-elastic-plate-with-hole/summarise_results.py"
        }
    ],
    "result": [
        {
            "@id": "#task/1cc8abe917eea617237b37eb263499f7/summary.json"
        }
    ],
    "actionStatus": "http://schema.org/CompletedActionStatus"
},     
```
Then, part of the query + results for the specific node `#task/1cc8abe917eea617237b37eb263499f7` would be:

```sparql
SELECT *
WHERE {
  GRAPH <https://w3id.org/ro-id-dev/c87448ad-5e9a-49fa-85e5-1fed9ecf9709/.ro/annotations/c45c44b2-3afb-4059-9505-25fc03b60139.ttl> {
    <http://w3id.org/ro-id/rohub/model#task/1cc8abe917eea617237b37eb263499f7> ?p ?o .
  }
}
```

|    ?p    |    ?o    |
|----------|----------|
| http://xmlns.com/foaf/0.1/name     | "summary (1)"     |
| http://schema.org/result     | "#task/1cc8abe917eea617237b37eb263499f7/summary.json"     |
| http://schema.org/actionStatus     | http://schema.org/CompletedActionStatus     |
| http://schema.org/agent     | https://orcid.org/0000-0000-0000-0000     |
| http://www.w3.org/1999/02/22-rdf-syntax-ns#type    | http://schema.org/CreateAction    |
| http://schema.org/object     | "home/runner/work/NFDI4IngModelValidationPlatform/NFDI4IngModelValidationPlatform/benchmarks/linear-elastic-plate-with-hole/summarise_results.py"     |









