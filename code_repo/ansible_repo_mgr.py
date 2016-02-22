import json
from pymongo import MongoClient
from ansible_repo import AnsibleRepo, AnsibleRepoEncoder


class AnsibleRepoManager(object):
    def __init__(self, config={}):
        self._repos = dict()
        mongo_host = config.get('mongo-host') if 'mongo-host' in config else 'localhost'
        mongo_port = config.get('mongo-port') if 'mongo-port' in config else 27017
        mongo_db = config.get('mongo-db') if 'mongo-db' in config else 'ansible_db'
        mongo_col = config.get('mongo-col') if 'mongo-col' in config else 'repos'
        self.mongo_client = MongoClient(mongo_host, mongo_port)
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


if __name__ == '__main__':
    import yaml
    repo = AnsibleRepo()
    test_layout = yaml.load(open('sample_layout.yaml').read())
    repo.load_from_local('/Users/akimotoakira/Box/git/icos-cd-services-deployer/', test_layout)
    repo.generate_metadata()
    print json.dumps(repo, cls=AnsibleRepoEncoder)
    mgr = AnsibleRepoManager()
    mgr.save_to_db(repo)