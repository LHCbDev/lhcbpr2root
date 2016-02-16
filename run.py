# =============================================================================
# STD:
# =============================================================================
import os
import json
from dotenv import load_dotenv
# OTHER:
# =============================================================================
import ROOT
from flask import (Flask, request, abort, jsonify, current_app)
from functools import wraps


# =============================================================================
os.environ.setdefault('ENV', 'default')
env_file = os.path.abspath(os.path.join('envs', "%s.env" % os.getenv('ENV')))
print('*' * 80)
print("Read environment from '{}'".format(env_file))
load_dotenv(env_file)


# =============================================================================
# Constants:
# =============================================================================
ROOT_DATA = os.path.abspath(os.getenv(
    'ROOT_DATA',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
))
print("Path to ROOT directory '{}'".format(ROOT_DATA))
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_HOST = os.getenv('FLASK_HOST', None)
KEY_FILES = 'files'
KEY_ITEMS = 'items'
DELIM = ','
DEBUG = True
# =============================================================================
app = Flask("ROOT service")
app.debug = DEBUG
print('*' * 80)

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
    obj = root.FindObjectAny(item)
    if obj:
        obj_json = json.loads(str(ROOT.TBufferJSON.ConvertToJSON(obj)))
        return obj_json
    return None


def process_file(filename, items):

    filename_abs = os.path.join(ROOT_DATA, filename)
    if os.path.isfile(filename_abs):
        root = ROOT.TFile.Open(filename_abs, "READ")
        if not root:
            return None
        json_items = {}
        for item in items:
            json_item = process_item(root, item)
            if json_item:
                json_items[item] = json_item
        return {"root": filename, "items": json_items}
    else:
        print("File '%s' does not exists" % filename_abs)
    return None


# =============================================================================
# Routes:
# =============================================================================


@app.route('/')
@jsonp
def service():
    """ Main service """
    result = []
    # -------------------------------------------------------------------------
    files = request.args.get(KEY_FILES, None)
    items = request.args.get(KEY_ITEMS, '')
    if not files:
        abort(404)

    # -------------------------------------------------------------------------
    for f in files.split(DELIM):
        json_file = process_file(f, items.split(DELIM))
        if json_file:
            result.append(json_file)

    # -------------------------------------------------------------------------
    return jsonify(result=result)

if __name__ == '__main__':

    app.run(host=FLASK_HOST, port=FLASK_PORT)
