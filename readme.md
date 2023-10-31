Please review the KB [Artifactory Cleanup Best Practices](https://jfrog.com/knowledge-base/artifactory-cleanup-best-practices/)

For Artifactory Cleanup , you can search using  JFrog CLI for artifacts you want to delete in Artifactory  using:
- a [FileSpec](https://www.jfrog.com/confluence/display/JFROG/Using+File+Specs) for [Searching Files](https://www.jfrog.com/confluence/display/CLI/CLI+for+JFrog+Artifactory#CLIforJFrogArtifactory-SearchingFiles)  

Example: `jf rt s --spec <xyz.spec>`.

-   [AQL](https://www.jfrog.com/confluence/display/JFROG/Artifactory+Query+Language)  using the 
`/api/search/aql` REST API. 

**Note:** When using [AQL](https://www.jfrog.com/confluence/display/JFROG/Artifactory+Query+Language) inside a 
[FileSpec](https://www.jfrog.com/confluence/display/JFROG/Using+File+Specs) you cannot specify the attributes to
include in the output . The following attributes will always be included:

`.include("name","repo","path","actual_md5","actual_sha1","sha256","size","type","modified","created","property")`

# Here are some examples:

### All files not downloaded for 3 months in a repository using FileSpec:
[artifacts_not_downloaded_for_3months.spec](./parameterize_repo_name/artifacts_not_downloaded_for_3months.spec)
```bash
jf rt s --spec parameterize_repo_name/artifacts_not_downloaded_for_3months.spec --spec-vars "RepoName=asaf-test" 
```
**Note:** Executing  the below command will list  the files (matched by the filespec) not downloaded
for 3 months and will interactively ask for deletion. Entering  'Y' at this point in the CLI will
delete those files.

```bash
jf rt del --spec parameterize_repo_name/artifacts_not_downloaded_for_3months.spec --spec-vars "RepoName=asaf-test" 
```

---

### Find docker images not downloaded or updated for 3 months:
[docker_tags_not_downloaded_for_3_months.spec](./cleanup_unused_docker_image_tag/docker_tags_not_downloaded_for_3_months.spec)

```text
jf rt s --spec cleanup_unused_docker_image_tag/docker_tags_not_downloaded_for_3_months.spec \
--spec-vars "RepoName=docker-dev-local"
```

**Note:** Executing  the below command will list  the **manifest.json**  of all docker images not downloaded 
for 3 months and will interactively ask for deletion. Do not enter 'Y' at this point in the CLI as  it will 
delete only the manifest.json . We want to delete the full docker tag and not just the **manifest.json**.

```textmate
jf rt del --spec cleanup_unused_docker_image_tag/docker_tags_not_downloaded_for_3_months.spec \
--spec-vars "RepoName=demoreg"
```

### To delete the full docker tag do the following:

#### Cleanup docker images
1. Verify the docker images to cleanup

 Filespec:   [docker_tags_not_downloaded_for_3_months.spec](./cleanup_unused_docker_image_tag/docker_tags_not_downloaded_for_3_months.spec)
```textmate
jf rt s --spec cleanup_unused_docker_image_tag/docker_tags_not_downloaded_for_3_months.spec --spec-vars \
   "RepoName=demoreg;time_range=3mo" |  jq -r '.[].path'
```


2. Do the cleanup:
```text
for manifest in $(jf rt s --spec cleanup_unused_docker_image_tag/docker_tags_not_downloaded_for_3_months.spec \
--spec-vars "RepoName=demoreg;time_range=3mo" |  jq -r '.[].path'); do
   tag=$(echo $(dirname "${manifest}"))
   printf "deleting ${tag}\n"
   tag_deleted=$(yes| jf rt del "${tag}")
   printf "deleted ${tag_deleted}\n"
done
```



#### Cleanup Docker tag using **AQL** from Python script

You can also use the python script [clean_docker.py](./cleanup_unused_docker_image_tag/clean_docker.py)
that was improvised from KB [How to clean up old Docker images](https://jfrog.com/knowledge-base/how-to-clean-up-old-docker-images/)

```textmate
python clean_docker.py http://localhost:8081/artifactory admin password my-docker-repo 3mo
```

---
### Find  all artifacts in a repo which were updated before 3 months but were never downloaded , or  were downloaded before 3 months. 
**Use-case:** Since no one downloaded these artifacts recently , they may be good candidates for deletion. 

For example: a dev repo which has lots of uploads and needs aggressive cleanup.

**Note:** To cleanup  Federated repos use "updated" instead of "stat.downloaded" in below aql because of 
[RTFACT-26646](https://jfrog.atlassian.net/browse/RTFACT-26646)
```bash
curl -s -XPOST  https://example.jfrog.io/artifactory/api/search/aql -u**** -H 'Content-Type: text/plain'  -d 'items.
find({
                   "repo": { "$eq": "libs-release-local"
                    },
                     "type":  "file",
                    "$or":[
                        {
                            "$and": [
                                { "stat.downloads": { "$eq":null } },
                                { "updated": { "$before": "3mo" } }
                            ]
                        },
                        {
                            "$and": [
                                { "stat.downloads": { "$gt": 0 } },
                                { "stat.downloaded": { "$before": "3mo" } }
                            ]
                        }
                    ]
                }).include("repo", "path", "name", "size", "actual_sha1", "sha256", "created", "modified", "updated", "created_by", "modified_by", "stat.downloaded", "stat.downloads")'
```
or:
```text
jf rt curl -s -XPOST /api/search/aql -H 'Content-Type: text/plain' -d 'items.find({
                   "repo": { "$eq": "asaf-test"
                    },
                     "type":  "file",
                    "$or":[
                        {
                            "$and": [
                                { "stat.downloads": { "$eq":null } },
                                { "updated": { "$before": "3mo" } }
                            ]
                        },
                        {
                            "$and": [
                                { "stat.downloads": { "$gt": 0 } },
                                { "stat.downloaded": { "$before": "3mo" } }
                            ]
                        }
                    ]
                }).include("repo", "path", "name", "size", "actual_sha1", "sha256", "created", "modified", "updated", "created_by", "modified_by", "stat.downloaded", "stat.downloads")'
```
---

### How to parameterize the repository name in AQL ?

``` bash
REPO=libs-release-local
jf rt curl -s -XPOST /api/search/aql -H 'Content-Type: text/plain' -d "items.find({ \"repo\": { \"\$eq\":\"${REPO}\" }, \"type\": \"file\", \"\$or\":[ { \"\$and\": [ { \"stat.downloads\": { \"\$eq\":null } }, { \"updated\": { \"\$before\": \"3mo\" } } ] }, { \"\$and\": [ { \"stat.downloads\": { \"\$gt\": 0 } }, { \"stat.downloaded\": { \"\$before\": \"3mo\" } } ] } ] }).include(\"repo\", \"path\", \"name\", \"size\", \"actual_sha1\", \"sha256\", \"created\", \"modified\", \"updated\", \"created_by\", \"modified_by\", \"stat.downloaded\", \"stat.downloads\")"
```
or
```text
repositoryName="asaf-test"
curl -s -XPOST https://example.jfrog.io/artifactory/api/search/aql -usureshv -H 'Content-Type: text/plain' -d 'items.
find({
                   "repo": { "$eq": "'"${repositoryName}"'"
                    },
                     "type":  "file",
                    "$or":[
                        {
                            "$and": [
                                { "stat.downloads": { "$eq":null } },
                                { "updated": { "$before": "3mo" } }
                            ]
                        },
                        {
                            "$and": [
                                { "stat.downloads": { "$gt": 0 } },
                                { "stat.downloaded": { "$before": "3mo" } }
                            ]
                        }
                    ]
                }).include("repo", "path", "name", "size", "actual_sha1", "sha256", "created", "modified", "updated", "created_by", "modified_by", "stat.downloaded", "stat.downloads")'
```
or
```text
repositoryName="asaf-test"
jf rt curl -s -XPOST /api/search/aql -H 'Content-Type: text/plain' -d 'items.find({
                   "repo": { "$eq": "'"${repositoryName}"'"
                    },
                     "type":  "file",
                    "$or":[
                        {
                            "$and": [
                                { "stat.downloads": { "$eq":null } },
                                { "updated": { "$before": "3mo" } }
                            ]
                        },
                        {
                            "$and": [
                                { "stat.downloads": { "$gt": 0 } },
                                { "stat.downloaded": { "$before": "3mo" } }
                            ]
                        }
                    ]
                }).include("repo", "path", "name", "size", "actual_sha1", "sha256", "created", "modified", "updated", "created_by", "modified_by", "stat.downloaded", "stat.downloads")'  
```
or
```text
or

repositoryName="asaf-test"
query='items.find({
    "repo": { "$eq": "'"${repositoryName}"'" },
    "type": "file",
    "$or": [
        {
            "$and": [
                { "stat.downloads": { "$eq": null } },
                { "updated": { "$before": "3mo" } }
            ]
        },
        {
            "$and": [
                { "stat.downloads": { "$gt": 0 } },
                { "stat.downloaded": { "$before": "3mo" } }
            ]
        }
    ]
}).include("repo", "path", "name", "size", "actual_sha1", "sha256", "created", "modified", "updated", "created_by", "modified_by", "stat.downloaded", "stat.downloads")'
jf rt curl -s -XPOST /api/search/aql -H 'Content-Type: text/plain' -d "${query}"
```
or
```text

repositoryName="asaf-test"
query=$(cat query_with_REPO_NAME.aql | sed "s/REPO_NAME/$repositoryName/g")
jf rt curl -s -XPOST /api/search/aql -H 'Content-Type: text/plain' -d "$query"
```


---

### Find artifacts with names ending in "*filelists.xml.gz" and matching a specific "path" : 
Example using AQL inline
```text
curl -u $MYUSER:$MYPASSWORD -XPOST  -H 'Content-Type: text/plain' http://$MYSERVERHOST_IP/artifactory/api/search/aql  -d 'items.find({ "repo": "local-goldimages-legacy-generic-aws-us-east-1", "path": { "$match": "http:/*" }, "name": { "$match": "*filelists.xml.gz" } }).include("repo", "path", "name", "size", "actual_sha1", "sha256", "created", "modified", "updated", "created_by", "modified_by", "stat.downloaded", "stat.downloads")'
```
or

using a file containing the AQL : [item_search.aql](./item_search.aql)

```bash
curl -u $MYUSER:$MYPASSWORD -XPOST  -H 'Content-Type:text/plain' http://$MYSERVERHOST_IP/artifactory/api/search/aql  -T item_search.aql
```

### Find Aqls that were run  when using  "jf transfer-files":

a) Grep the jf logs as follows to get aqls:
```text
grep  "Searching Artifactory using AQL query\|Done transferring folder" ~/.jfrog/logs/jfrog-cli.2022-08-06.16-27-44.31234.log > Searching_Done.txt
```
b) Then you can execute the aql :
```text
curl -H "Authorization: Bearer  $MYTOKEN" -XPOST  -H 'Content-Type: text/plain' http://$MYSERVERHOST_IP/artifactory/api/search/aql  -d 'items.find({"type":"any","$or":[{"$and":[{"repo":"local-trashcan-generic-us-east-1","path":{"$match":"jenkins-generic-remote-us-west-2-legacy-cache/dev-tools"},"name":{"$match":"*"}}]}]}).include("repo","path","name","type").sort({"$asc":["name"]}).offset(0).limit(10000)'
```

