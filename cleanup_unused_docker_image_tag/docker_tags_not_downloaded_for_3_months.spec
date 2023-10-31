{
  "files": [
    {
      "aql": {
        "items.find":{
                   "repo": {  "$eq": "${RepoName}"
                    },
                     "type":  "file",
                     "name": {
                                             "$eq": "manifest.json"
                                         },
                    "$or":[
                        {
                            "$and": [
                                { "stat.downloads": { "$eq":null } },
                                { "updated": { "$before": "${time_range}" } }
                            ]
                        },
                        {
                            "$and": [
                                { "stat.downloads": { "$gt": 0 } },
                                { "stat.downloaded": { "$before": "${time_range}" } }
                            ]
                        }
                    ]
        }

      }
    }
  ]
}