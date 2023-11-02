[SaaS_migration_cleanup](https://docs.google.com/document/d/1VdafCaAjkpplHbWco1R6OpMY2VqQJKu_kJ0o16tySIo/edit#)

Detect top 10 largest repositories in size (non docker)
```text
jf rt curl api/storageinfo |\
jq '
   [
       .repositoriesSummaryList[] |
       select(.repoType=="LOCAL") |
       select(.packageType!="Docker")
   ]|
   sort_by(.usedSpaceInBytes) |
   .[-10:] |
   reverse
'
```
---

Find the artifact with largest / biggest size:
https://jfrog.com/help/r/how-to-find-the-largest-files-in-artifactory
```text
jf rt curl -X POST /api/search/aql -H "Content-Type: text/plain"  -d 'items.find({"name" : {"$match":"*"}}).include("size").sort({"$desc": ["size"]}).limit(1)'

or

jf rt curl -X POST   -H "Content-Type: text/plain" /api/search/aql -d 'items.find({"type":"file"}).sort({"$desc":["size"]}).limit(10)'

```

---

With a very large repository, you can make use of the AQL query to find and delete the unused artifacts in batches manually.

Here is an Example query:
```text
jf rt curl -X POST -H "Content-Type:text/plain" -d 'items.find({"repo":{"$eq":"ams"},"created" : {"$lt" : "2019-01-01"},
"type":"file","size":{"$gt":"50000000"},"stat.downloaded":{"$lt" : "2019-01-01"},"$or":[{"name":{"$match":"*"}}]}).sort
({"$desc":["size","name"]}).limit(10)' /api/search/aql | jq '.results[].name'|cut -d \" -f2
```
---
