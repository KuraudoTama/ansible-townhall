from flask import request, Response

from code_repo.ansible_repo_mgr import AnsibleRepoManager
from . import repo_api

repo_mgr = AnsibleRepoManager()
repo_mgr.rebuild_from_db()


@repo_api.route("/api/v1/repos", methods=['GET', 'POST'])
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
        pass


@repo_api.route("/api/v1/repos/<repo_name>", methods=['GET', 'PUT', 'DELETE'])
def repo_operations(repo_name):
    if request.method == 'GET':
        repo = repo_mgr.get_repo(repo_name)
        return Response(repo, mimetype='application/json')


@repo_api.route("/api/v1/playbooks/<playbook_id>", methods=['GET'])
def get_playbook(playbook_id):
    pass
