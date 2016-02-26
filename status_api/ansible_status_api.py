from flask import Response
from flask.ext.cors import cross_origin

from code_repo.ansible_repo_mgr import AnsibleRepoManager
from utilities.web_util import crossdomain
from . import repo_api

repo_mgr = AnsibleRepoManager()
repo_mgr.rebuild_from_db()

common_header = {'Content-Type': 'text/json', 'Access-Control-Allow-Origin': '*'}


@repo_api.route("/api/status", methods=['GET'])
@crossdomain(origin='*')
@cross_origin(origin='*')
def status_info():
    return Response({'http': 'ok'}, mimetype='application/json')
