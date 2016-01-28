class AnsibleRepoManager(object):
    def __init__(self):
        self._repos = dict()

    def add_repo(self, repo):
        self._repos[repo.repo_name] = repo

    def remove_repo(self, repo_name):
        self._repos.pop(repo_name)

    def list_repos(self):
        return self._repos
