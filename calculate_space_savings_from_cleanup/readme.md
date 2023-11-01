
# Artifactory Cleanup Script

This Python script is designed to help you calculate the space saving if you clean up artifacts in an Artifactory repository based on  an aql.

## Prerequisites

Before using this script, make sure you have the following prerequisites installed and configured:

- Python: This script is written in Python and requires Python to be installed on your system.

- Artifactory CLI (JFrog CLI): You need to have JFrog CLI installed and configured with access to your Artifactory instance. You can download and configure JFrog CLI from [here](https://www.jfrog.com/getcli/).

## Usage

To use the script, follow the syntax below:

```bash
python spacesavings.py --repoName <RepoName> --downloadedOlderThan <Duration>  [--serverID <ServerID>] [--dryRun <true/false>]
```

### Options:

- `--repoName` (Mandatory): Specify the name of the Artifactory repository from which you want to clean up artifacts.

- `--downloadedOlderThan` (Mandatory): Set the duration (e.g., 1d, 1w, 1mo, 1y) to define the age threshold for artifacts to be considered for cleanup.

- `--dryRun` (Optional): Set this option to 'true' to perform a dry run, which means the script will simulate the cleanup without actually deleting artifacts. If not provided or set to 'false', the script will perform the actual deletion. Default is 'false'.

- `--serverID` (Optional): Set the Artifactory server ID (default is 'proservices'). You can specify a different server ID if you have multiple Artifactory configurations in your JFrog CLI configuration file.

### Examples:

1. Perform a dry run to simulate cleanup:
   ```bash
   python spacesavings.py --repoName docker-local --downloadedOlderThan 1y --dryRun true
   ```

2. Perform an actual cleanup without a dry run:
   ```bash
   python spacesavings.py --repoName docker-local --downloadedOlderThan 15w
   ```

## How it Works

The script uses the Artifactory API to search for artifacts in the specified repository that match the defined criteria. It identifies artifacts based on their download statistics and the last time they were updated. The script then calculates the total size of artifacts that meet the criteria and provides an estimate of the space savings that can be achieved by cleaning up these artifacts.

## Error Handling

If any errors occur during the execution of the script, error messages will be displayed to help diagnose the issue. You can refer to these error messages to troubleshoot and resolve any problems.
