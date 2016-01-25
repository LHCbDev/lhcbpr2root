# CERN ROOT's http server in python

This web server returns objects from **ROOT** files in **json** format

## Request example

```
/?files=file1,file2,file3&items=item1,item2
```
## Response example
```json
{
  "result": [
    {
      "items": {
        "item1": {
          "_typename": "TGraph",
          ...
        },
        "item2": {
          "_typename": "TGraph",
          ...
        }
      },
      "root": "file1"
    },
    {
      "items": {
        "item1": {
          "_typename": "TGraph",
          ...
        },
        "item2": {
          "_typename": "TGraph",
          ...
        }
      },
      "root": "file2"
    }
  ]
}
```
