from . import repo_api


@repo_api.route("/api/v1/repos", methods=['GET', 'POST'])
def repos_collection():


    return 'hi ansible'


@repo_api.route("/api/v1/repos/<repo_name>", methods=['GET'])
def get_repo(repo_name):
    pass


@repo_api.route("/api/v1/playbooks/<playbook_id>", methods=['GET'])
def get_playbook(playbook_id):
    pass
