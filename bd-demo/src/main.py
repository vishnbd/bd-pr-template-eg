import os
import requests

from artifactory.artifact import lookup_artifact, copy_artifact

artifactory_url = os.getenv("ARTIFACTORY_URL", "")
api_key = os.getenv("ARTIFACTORY_API_KEY", "")
remote_repo = os.getenv("REMOTE_REPO", "bd-demo-pypi-remote-cache")
dest_repo = os.getenv("DEST_REPO", "bd-demo-pypi-local")
BINARIES_FOLDER = os.getenv("BINARIES_FOLDER", ".binaries")


def get_whl_files(directory):
    """
    Fetches the list of all files with the '.whl' extension in the specified directory.

    Args:
        directory (str): Path to the directory to search.

    Returns:
        list: A list of full file names (with extensions) of all '.whl' files in the directory.
    """
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"The directory '{directory}' does not exist.")

    whl_files = []
    for file_name in os.listdir(directory):
        if file_name.endswith(".whl"):
            whl_files.append(file_name)

    return whl_files


def main():

    binaries_folder = BINARIES_FOLDER
    try:
        whl_files = get_whl_files(binaries_folder)
        print("Found .whl files:")
        for whl_file in whl_files:
            print(whl_file)
            try:
                artifact_name = whl_file                
                # Check if the artifact exists in the destination repository
                exists = lookup_artifact(artifactory_url, dest_repo, artifact_name, api_key)
                if exists:
                    print("Artifact found in the destination repository.")
                else:
                    print("Artifact not found in the destination repository. Attempting to copy from the remote repository...")

                    # Check if the artifact exists in the destination repository
                    artifact_path = lookup_artifact(artifactory_url, remote_repo, artifact_name, api_key)

                    # Copy the artifact from the remote repository to the destination repository
                    copy_artifact(artifactory_url, remote_repo, dest_repo, artifact_path, api_key)
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
    except FileNotFoundError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
