import json
from flask import request, Response
from flask.ext.cors import CORS, cross_origin
from code_repo.ansible_repo_mgr import AnsibleRepoManager
from utilities.web_util import crossdomain
from utilities.config import ConfigReader
from . import repo_api

repo_mgr = AnsibleRepoManager()
repo_mgr.rebuild_from_db()

common_header = {'Content-Type': 'text/json', 'Access-Control-Allow-Origin': '*'}


@repo_api.route("/api/v1/repos", methods=['GET', 'POST'])
@crossdomain(origin='*')
@cross_origin(origin='*')
def repos_collection():
    """
    The POST data should be in this format:

    {
      "gitRepoUrl": <git repo url>,
      "gitBranch": <git branch>,    - Optional, default is master
      "layout": <the layout json data>,
      "localBasePath": <the local base path for the code repo>    - Optional
    }

    :return:
    """
    if request.method == 'GET':
        return Response(repo_mgr.list_repos(), mimetype='application/json')
    if request.method == 'POST':
        if request.data:
            repo_para = json.loads(request.data)
            if 'gitRepoUrl' not in repo_para or \
                            'layout' not in repo_para:
                return '{ "created":false, "message": "Parameters Error" }', 500
            result = repo_mgr.create_new_repo(repo_para.get('gitRepoUrl'),
                                              repo_para.get('layout'),
                                              git_branch=repo_para.get('gitBranch'),
                                              local_base_path=repo_para.get('localBasePath'))

            return Response(json.dumps(result),
                            mimetype='application/json')


@repo_api.route("/api/v1/logs/<repo_name>", methods=['GET'])
def repo_logs(repo_name):
    log_path = '/etc/ansible-townhall/logs/'
    file_name = ''.join([log_path, 'gitlog.', repo_name])

    with open(file_name, 'r') as f:
        lines = f.readlines()

    content = {"repoName": repo_name,
               "logContent": lines[-1]}

    return Response(json.dumps(content), mimetype='application/json')


@repo_api.route("/api/v1/repos/<repo_name>", methods=['GET', 'PUT', 'DELETE'])
@cross_origin(origin='*')
def repo_operations(repo_name):
    if request.method == 'GET':
        repo = repo_mgr.get_repo(repo_name)
        return Response(repo, mimetype='application/json')
    if request.method == 'DELETE':
        repo_mgr.remove_repo(repo_name)
        return '{ "deleted":true, "message": "%s deleted" }' % repo_name, 200


@repo_api.route("/api/v1/playbooks/<playbook_id>", methods=['GET'])
def get_playbook(playbook_id):
    pass
