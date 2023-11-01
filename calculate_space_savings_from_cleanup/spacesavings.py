import subprocess
import json
import sys
import argparse
# python spacesavings.py --repoName jfrogpipelines --downloadedOlderThan 450d --serverID proservices

def usage():
    print("Unknown options:", sys.argv[1])
    print("Valid options are:")
    print("--repoName - [Mandatory] Repo Name")
    print("--downloadedOlderThan - [Mandatory] duration like 1d, 1w, 1mo, or 1y")
    print("--dryRun - [Optional] Set to 'true' to perform a dry run, set to 'false' or not provided to perform actual deletion (default).")
    print("--serverID - [Optional] Set the Artifactory server ID (default is 'proservices').")
    print("Example 1: python script.py --repoName docker-local --downloadedOlderThan 1y --dryRun true --serverID myserver")
    print("Example 2: python script.py --repoName docker-local --downloadedOlderThan 15w")
    sys.exit(1)



parser = argparse.ArgumentParser()
parser.add_argument("--repoName", help="[Mandatory] Repo Name", required=True)
parser.add_argument("--downloadedOlderThan", help="[Mandatory] duration like 1d, 1w, 1mo, or 1y", required=True)
parser.add_argument("--dryRun", help="[Optional] Set to 'true' to perform a dry run, set to 'false' or not provided to perform actual deletion (default).", default="false")
parser.add_argument("--serverID", help="[Optional] Set the Artifactory server ID (default is 'proservices').", default="proservices")
args = parser.parse_args()

repo = args.repoName
olderthan = args.downloadedOlderThan
dryRun = args.dryRun
serverID = args.serverID

aql_url="api/search/aql"
aql_info = f"""
items.find({{
    "repo": {{"$eq": "{repo}"}},
    "type": "file",
    "$or": [
        {{
            "$and": [
                {{"stat.downloads": {{"$eq": null}}}},
                {{"updated": {{"$before": "{olderthan}"}}}}
            ]
        }},
        {{
            "$and": [
                {{"stat.downloads": {{"$gt": 0}}}},
                {{"stat.downloaded": {{"$before": "{olderthan}"}}}}
            ]
        }}
    ]
}}).include("path", "size", "stat.downloads", "stat.downloaded")
"""

# jf rt curl -s -XPOST "${aql_url}" -H "content-type: text/plain" --data "$aql_info"
try:
    completed_process = subprocess.run(
        ["jf", "rt", "curl", "-s", "-XPOST", aql_url, "-H",  "content-type: text/plain", "--data" , aql_info, "--server-id", serverID],
        capture_output=True,
        text=True,
        check=True
    )

    results = json.loads(completed_process.stdout).get('results', [])
    total_size_bytes = sum(result['size'] for result in results)
    total_size_mb = total_size_bytes / (1024 * 1024)
    print("Total Size expected to be saved after cleanup (MB):", total_size_mb)
    
    # Print the results JSON
    # print("Results JSON:")
    # print(json.dumps(results, indent=4))
    
except subprocess.CalledProcessError as e:
    print("Error:", e.returncode, e.stderr)
except Exception as e:
    print("An error occurred:", str(e))
