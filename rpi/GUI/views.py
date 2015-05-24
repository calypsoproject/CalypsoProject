import json
import os
from flask import send_file
from GUI import app
import urllib


@app.route('/', defaults={'path': 'main.html'})
@app.route('/<path:path>')
def serve_file(path):
    return send_file(os.path.join(os.getcwd(), 'GUI/static', path))

@app.route('/api/<path:req>')
def api(req):
    result = None
    req = urllib.unquote(req)
    app.config["calypso"].logger.verbose('views.py/api', req)
    try:
        exec 'result = app.config["calypso"].' + req
        result = json.dumps(result)
    except Exception, e:
        result = json.dumps('exception: ' + str(e))
    return result

@app.route('/api/raw/<path:req>')
def raw_api(req):
    req = urllib.unquote(req)
    app.config["calypso"].logger.verbose('views.py/raw_api', req)
    self = app.config["calypso"]
    result = None
    try:
        exec req
    except Exception, e:
        result = e
    return repr(result)