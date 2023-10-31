{
  "files": [
    {
      "aql": {
        "items.find": {
          "repo": {
            "$eq": "${RepoName}"
          },
          "type": "file",
          "$or": [
            {
              "$and": [
                {
                  "stat.downloads": {
                    "$eq": null
                  }
                },
                {
                  "updated": {
                    "$before": "3mo"
                  }
                }
              ]
            },
            {
              "$and": [
                {
                  "stat.downloads": {
                    "$gt": 0
                  }
                },
                {
                  "stat.downloaded": {
                    "$before": "3mo"
                  }
                }
              ]
            }
          ]
        }
      }
    }
  ]
}