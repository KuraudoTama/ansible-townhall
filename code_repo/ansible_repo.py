import os
import re
import shutil
import json
from json import JSONEncoder

import yaml
from git import Repo

from ansible_objects import *


class InvalidGitRepoUrlException(Exception):
    def __init__(self, git_repo_url):
        self.git_repo_url = git_repo_url


class AnsibleRepoEncoder(JSONEncoder):
    def default(self, o):
        return {
            "inventories": json.loads(json.dumps(o.inventories, cls=AnsibleInventoryEncoder)),
            "playbooks": json.loads(json.dumps(o.playbooks, cls=AnsilePlaybookEncoder)),
            "roles": json.loads(json.dumps(o.roles, cls=AnsibleRoleEncoder))
        }


class AnsibleRepo(object):
    def __init__(self, git_repo_url=None, git_branch='master', layout=None, base_dir='/etc/ansible-townhall/repos/'):
        """
        Initialize an AnsibleRepo object.

        :param base_dir: The base directory to store the git repo
        :return: The instance
        """
        self._regex = '(\w+://)(.+@)*([\w\d\.]+)(:[\d]+){0,1}/*(.*/(.*)\.git)'

        self.base_dir = base_dir
        self.git_repo_url = git_repo_url
        self.git_branch = git_branch
        self._layout = layout

        self.repo_name = None
        self.repo_dir = None
        self.git_repo = None

        self.roles = None
        self.playbooks = None
        self.inventories = None

    def load(self, local_repo_path):
        self.repo_name = local_repo_path.rstrip('/').split('/')[-1]
        self.repo_dir = local_repo_path
        self.git_repo = Repo(local_repo_path)

    def clone(self, git_repo_url=None, git_branch='master'):
        """
        Clone the specified code repo to local store and generate metadata for it.

        :param git_repo_url: The URL of the git repo
        :param git_branch: The git branch to clone
        :return: True if everything is OK.
        """
        self.git_repo_url = git_repo_url
        if not self.git_repo_url:
            return False

        self.git_branch = git_branch

        self.repo_name = self._get_repo_name()
        self.repo_dir = ''.join([self.base_dir, self.repo_name])

        self._create_repo_directory()

        try:
            self.git_repo = Repo.clone_from(self.git_repo_url, self.repo_dir, branch=self.git_branch)
            return True
        except:
            return False

    def generate_metadata(self, layout=None):
        """
        Generate the metadata for the repo against a specified layout.

        :param layout: A JSON dict to specify the layout of the Ansible repo
        :return: The metadata
        """
        self._layout = layout
        if not self._layout:
            return None
        self.roles = self._process_roles(self._layout)
        self.playbooks = self._process_playbooks(self._layout)
        self.inventories = self._process_inventory(self._layout)

    def _process_inventory(self, layout):
        inventories = dict()
        if 'inventory' not in layout:
            return None
        pattern_type = layout['inventory']['type']
        if pattern_type == 'filenames':
            for filename in layout['inventory']['pattern'].split(','):
                inv_path = ''.join([self.repo_dir, layout['root'], filename])
                inventories[filename] = AnsibleInventory(inv_path)
            return inventories

    def _process_playbooks(self, layout):
        playbooks = dict()
        if 'playbooks' not in layout:
            return None
        pattern_type = layout['playbooks']['type']
        if pattern_type == 'regex':
            playbooks_dir = ''.join([self.repo_dir, layout['root']])
            for item in os.listdir(playbooks_dir):
                playbook_path = ''.join([playbooks_dir, item])
                if os.path.isfile(playbook_path) and re.match(layout['playbooks']['pattern'], item):
                    playbooks[item] = AnsiblePlaybook(playbook_path)

            return playbooks

    def _process_roles(self, layout):
        roles = dict()
        if 'roles' not in layout:
            return None
        pattern_type = layout['roles']['type']
        if pattern_type == 'dirnames':
            # TODO: support multiple directories
            roles_dir = ''.join([self.repo_dir, layout['root'], layout['roles']['pattern']])
            for directory in os.listdir(roles_dir):
                role = AnsibleRole(''.join([roles_dir, directory]))
                roles[role.name] = role
            return roles

    def _create_repo_directory(self):
        if os.path.exists(self.repo_dir):
            shutil.rmtree(self.repo_dir)

        os.mkdir(self.repo_dir)

    def _get_repo_name(self):
        m = re.match(self._regex, self.git_repo_url)
        if m:
            return m.groups()[-1]
        else:
            raise InvalidGitRepoUrlException(self.git_repo_url)


if __name__ == '__main__':
    repo = AnsibleRepo()
    repo.load('/Users/akimotoakira/Box/git/icos-cd-services-deployer/')
    layout = yaml.load(open('sample_layout.yaml').read())
    repo.generate_metadata(layout)

    print json.dumps(repo, cls=AnsibleRepoEncoder)
    import pdb

    pdb.set_trace()

    # repo = AnsibleRepo('https://github.com/KuraudoTama/pyslack.git', base_dir='.')
    # print repo.repo_dir
    # repo.clone()
