import requests


def lookup_artifact(artifactory_url, repo, artifact_name, api_key):
    """
    Looks for an artifact in an Artifactory repository.

    Args:
        artifactory_url (str): Base URL of the Artifactory server.
        repo (str): Name of the repository in Artifactory.
        artifact_name (str): Name of the artifact to look up.
        api_key (str): API key for authentication.

    Returns:
        bool: True if the artifact exists, False otherwise.

    Raises:
        requests.exceptions.RequestException: If the lookup request fails.
    """
    url = f"{artifactory_url}/artifactory/api/search/artifact?name={artifact_name}&repos={repo}"
    headers = {"X-JFrog-Art-Api": api_key}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            if "results" in data:
                for result in data["results"]:
                    if "uri" in result and artifact_name in result["uri"]:
                        print(f"Artifact '{artifact_name}' exists in repository '{repo}'.")
                        print(f"URI: {result['uri']}")
                        return extract_artifact_path(result['uri'], repo)
            print(f"Artifact '{artifact_name}' does not exist in repository '{repo}'.")
            return None
        elif response.status_code == 404:
            print(f"Artifact '{artifact_name}' does not exist in repository '{repo}'.")
            return None
        else:
            raise requests.exceptions.RequestException(
                f"Failed to look up artifact. Status code: {response.status_code}, Response: {response.text}"
            )
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Error during artifact lookup: {e}")


def extract_artifact_path(uri, repo_name):
    """
    Extracts the artifact's path from the given URI based on the repository name.

    Args:
        uri (str): The full URI of the artifact.
        repo_name (str): The name of the repository in the URI.

    Returns:
        str: The artifact's path relative to the repository, or None if the repository name is not found.
    """
    try:
        # Split the URI based on the repository name
        parts = uri.split(f"/{repo_name}/", 1)
        if len(parts) > 1:
            artifact_path = parts[1]
            return artifact_path
        else:
            print(f"Repository name '{repo_name}' not found in URI.")
            return None
    except Exception as e:
        print(f"Error extracting artifact path: {e}")
        return None


def copy_artifact(artifactory_url, remote_repo, dest_repo, artifact_path, api_key):
    """
    Copies an artifact from the remote repository to the destination repository.

    Args:
        artifactory_url (str): Base URL of the Artifactory server.
        remote_repo (str): Name of the remote repository in Artifactory.
        dest_repo (str): Name of the destination repository in Artifactory.
        artifact_path (str): Path of the artifact to copy.
        api_key (str): API key for authentication.

    Raises:
        requests.exceptions.RequestException: If the copy request fails.
    """
    copy_url = f"{artifactory_url}/artifactory/api/copy/{remote_repo}/{artifact_path}?to=/{dest_repo}/{artifact_path}"
    headers = {"X-JFrog-Art-Api": api_key}

    try:
        response = requests.post(copy_url, headers=headers)
        if response.status_code in (200, 201):
            print(f"Artifact '{artifact_path}' successfully copied from '{remote_repo}' to '{dest_repo}'.")
        else:
            raise requests.exceptions.RequestException(
                f"Failed to copy artifact. Status code: {response.status_code}, Response: {response.text}"
            )
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Error during artifact copy: {e}")
