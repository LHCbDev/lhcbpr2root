# =============================================================================
# STD:
# =============================================================================
import os
import json
# =============================================================================
# OTHER:
# =============================================================================
import ROOT

from flask import (Flask, request, abort)
from flask import jsonify
# =============================================================================
# Constants:
# =============================================================================
ROOT_DATA = os.getenv(
    'ROOT_DATA',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'))
KEY_FILES = 'files'
KEY_ITEMS = 'items'
DELIM = ','
DEBUG = True
# =============================================================================
app = Flask("ROOT service")
app.debug = DEBUG

# =============================================================================
# Functions:
# =============================================================================


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
    return None


# =============================================================================
# Routes:
# =============================================================================


@app.route('/')
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

    app.run()
