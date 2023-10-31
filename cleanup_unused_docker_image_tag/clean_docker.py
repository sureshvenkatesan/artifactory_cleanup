#!/usr/bin/env python
"""
Improvised from KB https://jfrog.com/knowledge-base/how-to-clean-up-old-docker-images/

This script searches for Docker images in a specified Artifactory repository that meet certain criteria and deletes them.
The script constructs an AQL query to find Docker image manifests that have not been downloaded in the last 3 months
or have been downloaded but have not been accessed in the last 3 months.
The script then retrieves the URL of each matching artifact and sends a DELETE request to delete the artifact.

Prerequisites :
pip install requests

Usage: python clean_docker.py BASE_URL USERNAME PASSWORD REPO_NAME

Arguments:
BASE_URL - the base URL of the Artifactory instance
USERNAME - the username for authentication
PASSWORD - the password for authentication
REPO_NAME - the name of the repository to search for Docker images
TIME_RANGE - the time range to use when searching for Docker images

Example: python clean_docker.py http://localhost:8081/artifactory admin password my-docker-repo 3mo
"""
import argparse
import requests


def clean_docker(base_url, user, password, repo, time_range):
    """
    Searches for all Docker images in a specified Artifactory repository that meet certain criteria and deletes them.
    The function constructs an AQL query to find Docker image manifests that have not been downloaded in the specified
    time range or have been downloaded but have not been accessed in the specified time range.
    The function then retrieves the URL of each matching artifact and sends a DELETE request to delete the artifact.

    Parameters:
    base_url (str): The base URL of the Artifactory instance.
    user (str): The username for authentication.
    password (str): The password for authentication.
    repo (str): The name of the repository to search for Docker images.
    time_range (str): The time range to use when searching for Docker images. The format should be <number><unit>,
                      where <number> is a positive integer and <unit> is one of "d" (days), "w" (weeks), "M" (months),
                      or "y" (years).

    Returns:
    None

    Raises:
    None
    """
    headers = {
        'content-type': 'text/plain',
    }

    data = f"""items.find({{
        "repo": {{"$eq":  "{repo}"     }},
        "type": "file",
        "name": {{
            "$eq": "manifest.json"
        }},
        "$or": [
            {{
                "$and": [
                    {{"stat.downloads": {{"$eq": null}} }},
                    {{"updated": {{"$before": "{time_range}"}} }}
                ]
            }},
            {{
                "$and": [
                    {{"stat.downloads": {{"$gt": 0}} }},
                    {{"stat.downloaded": {{"$before": "{time_range}"}} }}
                ]
            }}
        ]
    }} )"""

    myResp = requests.post(base_url+'api/search/aql', auth=(user, password), headers=headers, data=data)
    for result in eval(myResp.text)["results"]:
        print(result)
        # {'repo': 'demoreg', 'path': 'iot-demo/demo-ui/0.2', 'name': 'manifest.json', 'type': 'file',
        # 'size': 3031, 'created': '2021-05-02T12:08:22.569Z', 'created_by': 'eldada',
        # 'modified': '2021-05-02T13:20:11.694Z', 'modified_by': 'eldada', 'updated': '2022-10-26T22:25:02.879Z'}

        # get the docker image tag for the manifest.json
        docker_image_tag_url = base_url+ result['repo'] + '/' + result['path']
        print(docker_image_tag_url)
        # https://entplus.jfrog.io/artifactory/demoreg/iot-demo/demo-ui/0.2

        # Delete the Docker image tag for the manifest.json
        requests.delete(docker_image_tag_url, auth=(user, password))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('base_url', help='the base url of the Artifactory instance')
    parser.add_argument('user', help='the username for authentication')
    parser.add_argument('password', help='the password for authentication')
    parser.add_argument('repo', help='the repository name')
    parser.add_argument('time_range',
                        help='the time range to use when searching for Docker images. The format should be '
                             '<number><unit>, where <number> is a positive integer and <unit> is one of "d" (days),'
                             ' "w" (weeks), "mo" (months), or "y" (years). Ex: "3mo" means 3 months')

    args = parser.parse_args()
    clean_docker(args.base_url, args.user, args.password, args.repo, args.time_range)
