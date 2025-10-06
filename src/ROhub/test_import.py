import rohub
import pandas as pd

print("ROHub API URL:", rohub.settings.API_URL)
# loading credentials from external file
user_name = "joerg.unger@bam.de"
user_pwd = open("passwordROHub.txt").read()
rohub.login(
    username=user_name, password=user_pwd
)  # Ensure you are logged in to access ROHub features


# zip_path = "./metadata4ing_provenance.zip"
zip_path = "./nextflow_results_linear-elastic-plate-with-hole.zip"
resources_from_zip = rohub.ros_upload(path_to_zip=zip_path)

my_ros = rohub.list_my_ros()
if len(my_ros) == 0:
    print("Error fetching RO with id:", id, "creating a new one", e)
    ro_title = "The influence of eating habits on sleep"
    ro_research_areas = ["Medical science"]
    ro = rohub.ros_create(title=ro_title, research_areas=ro_research_areas)
    my_ros = rohub.list_my_ros()


# Assuming df is your pandas DataFrame with an "identifier" column
for index, row in my_ros.iterrows():
    id = row["identifier"]
    ro = rohub.ros_load(id)
    print("RO type:", ro.ros_type)
    if hasattr(ro, "title") and ro.title:
        print("RO title:", ro.title)
    if hasattr(ro, "authors") and ro.authors:
        print("RO authors:", ro.authors)
    if hasattr(ro, "description") and ro.description:
        print("RO description:", ro.description)
    if hasattr(ro, "research_areas") and ro.research_areas:
        print("RO research areas:", ro.research_areas)
    if hasattr(ro, "creation_date") and ro.creation_date:
        print("RO creation date:", ro.creation_date)
    if hasattr(ro, "last_modified_date") and ro.last_modified_date:
        print("RO last modified date:", ro.last_modified_date)
    if hasattr(ro, "doi") and ro.doi:
        print("RO DOI:", ro.doi)
    if hasattr(ro, "url") and ro.url:
        print("RO URL:", ro.url)
    if hasattr(ro, "metadata") and ro.metadata:
        print("RO metadata:", ro.metadata)
    print("RO metadata:", ro.show_metadata())
    print("---------------------------------")
