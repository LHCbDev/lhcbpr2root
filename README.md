# CERN ROOT's http server in python

This web server returns objects from **ROOT** files in **json** format
## Install
### Prerequisites
1. PYTHONPATH environment variable should contain path to ROOT lib directory
2. Python's major version should be the same as used for ROOT compilation

### Virtualenv
```sh
$> virtualenv venv
$> source venv/bin/activate
$> pip install
```
## Run
From application's folder:
```sh
$> python run.py
```

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
