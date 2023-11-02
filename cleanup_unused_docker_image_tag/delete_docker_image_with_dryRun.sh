#!/bin/bash
usage() {
  echo "Unknown options: $1
  Valid option are:
     --repoName - [Mandatory] Repo Name
     --downloadedOlderThan - [Mandatory] duration like 1d, 1w, 1mo or 1y
     --dryRun - [Optional] Set to 'true' to perform a dry run, set to 'false' or not provided to perform actual deletion (default).

  ex1: bash <script> --repoName docker-local --downloadedOlderThan 1y --dryRun true
  ex2: bash <script> --repoName docker-local --downloadedOlderThan 15w"
}
while [[ $# -gt 0 ]]; do
 case "$1" in
   --repoName)
     repo="$2"
     shift 2
     ;;
   --downloadedOlderThan)
     olderthan="$2"
     shift 2
     ;;
   --dryRun)
     dryRun="$2"
     shift 2
     ;;
   *)
     usage $1
     exit 1
     ;;
 esac
done

if [ -z "${repo}" ]; then
   echo "--repoName is unset or set to the empty string"
   usage
   exit 1
fi
if [ -z "${olderthan}" ]; then
   echo "--downloadedOlderThan is unset or set to the empty string"
   usage
   exit 1
fi

while true; do
read -p "Is [JF CLI] and [jq] installed and configured? (y/n) " yn

case $yn in
  [yY] ) echo Deleting docker images as per criteria;
    break;;
  [nN] ) echo Install [JF CLI] and [jq] and configure to your JPD;
    exit;;
  * ) echo invalid response;;
esac
done

aql_url="api/search/aql"

aql_info="items.find({
    \"repo\": {\"\$eq\": \"$repo\"},
    \"type\": \"file\",
    \"name\": {
        \"\$eq\": \"manifest.json\"
    },
    \"\$or\": [
        {
            \"\$and\": [
                {\"stat.downloads\": {\"\$eq\": null}},
                {\"updated\": {\"\$before\": \"$olderthan\"}}
            ]
        },
        {
            \"\$and\": [
                {\"stat.downloads\": {\"\$gt\": 0}},
                {\"stat.downloaded\": {\"\$before\": \"$olderthan\"}}
            ]
        }
    ]
}).include(\"path\")"
#get sha256 value


paths=$(jf rt curl -s -XPOST "${aql_url}" -H "content-type: text/plain" --data "$aql_info" | jq -r '.results[] | .path')
for path in $paths
do
    #Delete all layers and manifest file of a docker
    echo "Deleting Docker image $repo/$path"
    if [ "$dryRun" = "true" ]; then
        jf rt del --dry-run=true --quiet --threads 8 "$repo/$path/"
    else
        jf rt del --dry-run=false --quiet --threads 8 "$repo/$path/"
    fi

done
