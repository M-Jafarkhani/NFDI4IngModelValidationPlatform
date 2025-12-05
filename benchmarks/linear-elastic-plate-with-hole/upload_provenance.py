import argparse
import rohub
import time

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
        "--username",
        type=str,
        required=True,
        help="Username for RoHub",
    )
    parser.add_argument(
        "--password",
        type=str,
        required=True,
        help="Password for RoHub",
    )
    return parser.parse_args()


def run(args):
    USE_DEVELOPMENT_VERSION = True

    if USE_DEVELOPMENT_VERSION:
        rohub.settings.API_URL = "https://rohub2020-rohub.apps.paas-dev.psnc.pl/api/"
        rohub.settings.KEYCLOAK_CLIENT_ID = "rohub2020-cli"
        rohub.settings.KEYCLOAK_CLIENT_SECRET = "714617a7-87bc-4a88-8682-5f9c2f60337d"
        rohub.settings.KEYCLOAK_URL = "https://keycloak-dev.apps.paas-dev.psnc.pl/auth/realms/rohub/protocol/openid-connect/token"
        rohub.settings.SPARQL_ENDPOINT = (
            "https://rohub2020-api-virtuoso-route-rohub.apps.paas-dev.psnc.pl/sparql/"
        )

    rohub.login(args.username, args.password)

    identifier = ""

    try:
        upload_result = rohub.ros_upload(path_to_zip=args.provenance_folderpath)
        identifier = upload_result["identifier"]
    except KeyError as error:
        print(f"Error on Upload RoHub: {error}")
        exit(1)

    timeout_seconds = 5 * 60 
    poll_interval = 10
    start_time = time.time()

    while True:
        success_result = rohub.is_job_success(job_id=identifier)
        status = success_result.get("status", "UNKNOWN")

        if status == "SUCCESS":
            print(f"Upload successful: {success_result}")
            break
        elif time.time() - start_time > timeout_seconds:
            print(f"Upload did not succeed within 5 minutes. Last status: {status}")
            break
        else:
            print(f"Current status: {status}, waiting {poll_interval}s...")
            time.sleep(poll_interval)

def main():
    args = parse_args()
    run(args)


if __name__ == "__main__":
    main()
