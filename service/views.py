# =============================================================================
# STD:
# =============================================================================
import os
import ROOT
import json
from service import app, jsonp, utils
from flask import (request, abort, jsonify)

KEY_FILES = 'files'
KEY_ITEMS = 'items'
KEY_FOLDERS = 'folders'
KEY_COMPUTE = 'compute'
DELIM = '__'
ROOT_DATA = utils.root_data()

# =============================================================================
# Functions:
# =============================================================================


def process_item(root, item):
    """
    Tries to Get the object if fully qualified (i.e. complete path given)
    il fails tries a FindObjectAny which find object by name in the
    list of memory objects of the current directory or its sub-directories.
    Returns the JSON version of the object or None
    """
    obj = root.Get(str(item))

    if not obj:
        obj = root.FindObjectAny(str(item))
    if obj:
        obj_json = json.loads(str(ROOT.TBufferJSON.ConvertToJSON(obj)))
        return obj_json
    return None


def process_folder(root, path=""):
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
        topath = os.path.join(currentpath, mykey.GetName())
        gName = gName + "__" + mykey.GetName()
        if root.cd(topath):
            for key in ROOT.gDirectory.GetListOfKeys():
                filterKey(root, key, topath, toDict, gName)
    else:
        object_title = mykey.GetTitle()
        category = gName[2:]  # remove the first __
        if (not category in toDict.keys()):
            toDict[category] = {}
        if ":" in currentpath:
            toDict[category][os.path.join(
                currentpath.split(':')[1][1:].strip(), mykey.GetName())] = object_title
        else:
            toDict[category][
                os.path.join(currentpath, mykey.GetName())] = object_title
    return


def compute_opt(filenames, item, option):
    """
      Compute operation "option" on the item of the two files
      Implementing operations:
        Kolmogorov: calculate the kolmogorov test (returns its value with variable: "KSTest")
        Difference: calculate item1 - item2
        Ratio:      calculate item1 / item2
      Returns: { { "root": the first file name, "items": { "itemname": the first plots }},
                 { "root": the second file name, "items": { "itemname": the second plots }},
               "computed_result" or "KSTest": the computed plot/value }
    """
    if len(filenames) == 2:
        file1 = os.path.join(ROOT_DATA, filenames[0])
        file2 = os.path.join(ROOT_DATA, filenames[1])
        if not os.path.isfile(file1) or not os.path.isfile(file2):
            print("One of the given files '%s' or '%s' does not exists" %
                  (file1, file2))
            return None
        root1 = ROOT.TFile.Open(file1, "READ")
        root2 = ROOT.TFile.Open(file2, "READ")
        if not root1 or not root2:
            print("one of the fiven files '%s' or '%s' is not a root file" %
                  (file1, file2))
            return None

        result = []
        # first add the two histograms
        h1 = root1.Get(str(item))
        if h1:
            result.append({"root": filenames[0], "items": {
                          item: json.loads(str(ROOT.TBufferJSON.ConvertToJSON(h1)))}})
        else:
            print("ERROR item %s not found in file %s" % (item, file1))
            return None
        h2 = root2.Get(str(item))
        if h2:
            result.append({"root": filenames[1], "items": {
                          item: json.loads(str(ROOT.TBufferJSON.ConvertToJSON(h2)))}})
        else:
            print("ERROR item %s not found in file %s" % (item, file2))
            return None
        # compute what required
        if option == "Kolmogorov":
            result.append({"KSTest": h2.KolmogorovTest(h1)})
        if option == "Difference":
            h1.Add(h2, -1)
            h1.SetName("Difference")
            h1.SetOption("HIST")
            h1.SetMinimum(-100)
        elif option == "Ratio":
            h1.Divide(h2)
            h1.SetName("Ratio")
            h1.SetOption("HIST")
        if h1:
            result.append(
                {"computed_result": json.loads(str(ROOT.TBufferJSON.ConvertToJSON(h1)))})
        return result

    else:
        print("ERROR. We can compute the %s only beetween two files (given %s)" % (
            option, filenames))
    return None


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
      folders: list of directories to be parsed; for each folder returns two lists
      compute: computation to add to the result, possible labels are:
               "Kolmogorov", "Difference" and "Ratio"
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
    compute = request.args.get(KEY_COMPUTE, None)
    if not files:
        abort(404)

    # -------------------------------------------------------------------------
    if compute:
        for item in items.split(DELIM):
            json_file = compute_opt(files.split(DELIM), item, compute)
            if json_file:
                result += json_file
    else:
        for f in files.split(DELIM):
            json_file = process_file(
                f, items.split(DELIM), folders.split(DELIM))
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
