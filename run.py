KEY_FILES = 'files'
KEY_ITEMS = 'items'
DELIM = ','
DEBUG = True

import ROOT
from flask import Flask
from flask import request
app = Flask("ROOT service")
app.debug = DEBUG


@app.route('/')
def service():
    result = ""

    files = request.args.get(KEY_FILES, '')
    items = request.args.get(KEY_ITEMS, '')

    for f in files.split(DELIM):
        for item in items.split(DELIM):
            result += '%s-%s' % (f, item)
    return result
    # return flask.jsonify({'a': 'b', 'c': 'd'})

if __name__ == '__main__':

    app.run()
