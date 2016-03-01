from flask import Response
from flask.ext.cors import cross_origin
import json

from code_repo.ansible_repo_mgr import AnsibleRepoManager
from . import status_api

repo_mgr = AnsibleRepoManager()
repo_mgr.rebuild_from_db()

common_header = {'Content-Type': 'text/json', 'Access-Control-Allow-Origin': '*'}


@status_api.route("/api/status", methods=['GET'])
@cross_origin(origin='*')
def status_info():
    return Response(json.dumps({'http': 'ok'}), mimetype='application/json')
