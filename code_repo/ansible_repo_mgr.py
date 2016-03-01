import json

from pymongo import MongoClient

import common.settings as settings
from ansible_repo import AnsibleRepo, AnsibleRepoEncoder


class AnsibleRepoManager(object):
    def __init__(self):
        self._repos = dict()
        mongo_db = 'ansible_db'
        mongo_col = 'repos'
        self.mongo_client = MongoClient(settings.get_mongodb_url())
        self.db = self.mongo_client[mongo_db]
        self.collection = self.db[mongo_col]

    def rebuild_from_db(self):
        for repo_data in self.collection.find():
            repo = AnsibleRepo()
            repo.load_from_json(repo_data)
            repo.generate_metadata()
            self.add_repo(repo)

    def save_to_db(self, repo):
        repo_data = json.loads(json.dumps(repo, cls=AnsibleRepoEncoder))
        repo_data_db = self.collection.find_one({"name": repo_data["name"]})
        if repo_data_db is None:
            self.collection.insert(repo_data)
        else:
            self.collection.replace_one({"name": repo_data["name"]}, repo_data)

    def remove_from_db(self, repo_name):
        self.collection.delete_one({"name": repo_name})

    def add_repo(self, repo):
        self._repos[repo.name] = repo

    def remove_repo(self, repo_name):
        self.remove_from_db(repo_name)
        self._repos.pop(repo_name)

    def list_repos(self):
        return json.dumps(self._repos, cls=AnsibleRepoEncoder)

    def get_repo(self, repo_name):
        return json.dumps(self._repos.get(repo_name), cls=AnsibleRepoEncoder)

    def create_new_repo(self, git_repo_url, layout, git_branch='master',
                        local_base_path='/etc/ansible-townhall/repos/'):
        repo_data = self.collection.find_one({"gitRepoUrl": git_repo_url})
        if repo_data is not None:
            return {"created": False, "message": "Repository exists", "name": repo_data['name']}

        new_repo = AnsibleRepo()
        new_repo.load_from_git(git_repo_url, layout, git_branch, local_base_path)
        new_repo.generate_metadata()

        self.add_repo(new_repo)
        self.save_to_db(new_repo)

        new_repo_data = self.collection.find_one({"gitRepoUrl": git_repo_url})
        new_repo_data.pop('_id')
        new_repo_data.update({"created": True, "message": "Repository created"})
        return new_repo_data

