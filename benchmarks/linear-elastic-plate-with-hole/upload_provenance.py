import argparse
import rohub


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

    upload_result = rohub.ros_upload(path_to_zip=args.provenance_folderpath)

    print(upload_result)

def main():
    args = parse_args()
    run(args)


if __name__ == "__main__":
    main()
