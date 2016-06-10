# =============================================================================
# STD:
# =============================================================================
import os
import sys
import json
from dotenv import load_dotenv
# =============================================================================
# OTHER:
# =============================================================================
import ROOT

from flask import (Flask, request, abort, jsonify, current_app)
from functools import wraps

app = Flask("ROOT service")
# =============================================================================
def env_var(key, default=None):
    """Retrieves env vars and makes Python boolean replacements"""
    val = os.environ.get(key, default)
    if val == 'True':
        val = True
    elif val == 'False':
        val = False
    return val
# =============================================================================
os.environ.setdefault('ENV', 'default')
env_file = os.path.abspath(os.path.join('envs', "%s.env" % env_var('ENV')))
print('*' * 80)
print("Read environment from '{}'".format(env_file))
load_dotenv(env_file)


# =============================================================================
# Constants:
# =============================================================================
ROOT_DATA = os.path.abspath(env_var(
    'ROOT_DATA',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
))
print("Path to ROOT directory '{}'".format(ROOT_DATA))
FLASK_PORT = int(env_var('FLASK_PORT', 5000))
FLASK_HOST = env_var('FLASK_HOST', None)
KEY_FILES = 'files'
KEY_ITEMS = 'items'
KEY_FOLDERS = 'folders'
#DELIM = ','
DELIM = '__'
DEBUG = env_var('DEBUG', False)
# =============================================================================
# Functions:
# =============================================================================


def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function


def process_item(root, item):
    """
    Tries to Get the object if fully qualified (i.e. complete path given)
    il fails tries a FindObjectAny which find object by name in the
    list of memory objects of the current directory or its sub-directories.
    Returns the JSON version of the object or None
    """
    obj = root.Get(item)
    if not obj:
        obj = root.FindObjectAny(item)
    if obj:
        obj_json = json.loads(str(ROOT.TBufferJSON.ConvertToJSON(obj)))
        return obj_json
    return None


def process_folder(root, path = ""):
    """
    Reads recursively the directory trees inside the root file
    If path is defined returns the subtree of the given directory 
    Returns a dictionary (in "pathdir" / is substitutes with __):
    {
      "List__pathdir1": {
        "plotpath1.1" : "plottitle1.1".
        "plotpath1.2" : "plottitle1.2",
        ...
      },
      ...
      "List" : {
        "plotpath0.1" : "plottitle0.1",
        "plotpath0.2" : "plottitle0.2",
        ...
      }
    }
    Examples:  
    {
      "List__EcalMonitor": {
        "/EcalMonitor/143": "Number of Subhits in the ECAL ( BC = 2  )", 
        "/EcalMonitor/144": "Number of Subhits in the ECAL ( BC = 3  )", 
        "/EcalMonitor/145": "Number of Subhits in the ECAL ( BC = 4  )"
      }, 
      "List__Velo__VeloGaussMoni": {
        "/Velo/VeloGaussMoni/TOF": "Time Of Flight [ns]", 
        "/Velo/VeloGaussMoni/TOFPU": "PileUp: Time Of Flight [ns]"
      },
      "List": {
        "/ecalem": "E Ecal", 
        "/eop": "E/p" 
      }  
    } 
    """
    myDict = {}
    if path:
        if root.cd(path):
          for key in ROOT.gDirectory.GetListOfKeys():
              filterKey(root, key, path, myDict, "__List")
    else:
        for key in ROOT.gDirectory.GetListOfKeys():
            mypath = ROOT.gDirectory.GetPathStatic()
            filterKey(root, key, mypath, myDict, "")
            ROOT.gDirectory.cd(mypath)
    return myDict

def filterKey(root, mykey, currentpath, toDict, gName):
     if mykey.IsFolder():
        topath =  os.path.join(currentpath, mykey.GetName())
        gName = gName + "__" + mykey.GetName()
        if root.cd(topath):
          for key in ROOT.gDirectory.GetListOfKeys():
            filterKey(root, key, topath, toDict, gName)
     else:
        object_title = mykey.GetTitle()
        category = gName[2:] # remove the first __
        if ( not category in toDict.keys() ):
          toDict[category] = {}
        if ":" in currentpath:
          toDict[category][os.path.join(currentpath.split(':')[1][1:].strip(), mykey.GetName())] = object_title
        else:
          toDict[category][os.path.join(currentpath, mykey.GetName())] = object_title
     return


def process_file(filename, items, folders):
    """
    Process the list of items AND the list of folders for the given filename
    returns a dictionary:
      "root": the filename processed
      "items": a dictionary with all the processed items
      "trees": a dictionary with all the processed folders
    """
    filename_abs = os.path.join(ROOT_DATA, filename)
    if os.path.isfile(filename_abs):
        root = ROOT.TFile.Open(filename_abs, "READ")
        if not root:
            print("File '%s' is not a root file" % filename_abs)
            return None
        json_items = {}
        for item in items:
            json_item = process_item(root, item)
            if json_item:
                json_items[item] = json_item
        json_folders = {}
        for folder in folders:
          if folder != "":
            json_folder = process_folder(root, folder)
            if json_folder:
                json_folders[folder] = json_folder
        return {"root": filename, "items": json_items, "trees": json_folders}
    else:
        print("File '%s' does not exists" % filename_abs)
    return None


# =============================================================================
# Routes:
# =============================================================================

@app.route('/root/')
@jsonp
def service():
    """
    args:
      files: [REQUIRED] list of root files to be processed
      items: list of objects that need to be retrieved; first uses the Get function
             to retrieve it, if fails uses FindObjectAny, if fails again returns None
      folders: list of directories to be parsed; for each folder returns two lists:
              "folders" with the list of the Titles of the sub-directories and
              "objects" with the list of the Names of the objects inside the folder.
    returns "result", a list of dictionaries (one per file) with:
      "root": the filename processed
      "items": a dictionary with all the processed items
      "trees": a dictionary with all the processed folders
    """
    result = []
    # -------------------------------------------------------------------------
    files = request.args.get(KEY_FILES, None)
    items = request.args.get(KEY_ITEMS, '')
    folders = request.args.get(KEY_FOLDERS, '')
    if not files:
        abort(404)

    # -------------------------------------------------------------------------
    for f in files.split(DELIM):
        json_file = process_file(f, items.split(DELIM), folders.split(DELIM))
        if json_file:
            result.append(json_file)

    # -------------------------------------------------------------------------
    return jsonify(result=result)

def run_gunicorn_server(app):
    """run application use gunicorn http server
    """

    from gunicorn.app.base import Application

    class FlaskApplication(Application):
        def init(self, parser, opts, args):
            return {
                'bind': '{0}:{1}'.format(FLASK_HOST, FLASK_PORT),
                'workers': 4
            }

        def load(self):
            return app

    FlaskApplication().run()

def run_devel_server(app):
   app.run(host=FLASK_HOST, port=FLASK_PORT, debug=DEBUG)


if __name__ == '__main__':
    if "--gunicorn" in sys.argv:
        sys.argv.pop(sys.argv.index("--gunicorn"))
        run_gunicorn_server(app)
    else:
        run_devel_server(app)



