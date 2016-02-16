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
$> pip install -r requirements.txt
```
## Run
From application's folder:
```sh
$> python run.py
```

By default the application runs with environments loaded from `envs/default.env`. You can change it by setting the enveronments' file in ENV environment. For example:
```
$> ENV=default python run.py # Will load env/default.env
$> ENV=production python run.py # Will load env/production.env
```

### Configuration

The application configured through envirnment variables (see the section above). Default configuration:

```
ROOT_DATA=data
FLASK_PORT=8081
FLASK_HOST=0.0.0.0
DEBUG=True
```

* ROOT_DATA --- path to the root directory with ROOT files.
* FLASK_PORT and FLASK_HOST --- port and host for the web server
* DEBUG --- on/off debug mode


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
