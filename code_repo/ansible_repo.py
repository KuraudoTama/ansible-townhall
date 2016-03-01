import json
import os
import re
import shutil

from git import Repo, RemoteProgress

from common.ansible_objects import *


class InvalidGitRepoUrlException(Exception):
    def __init__(self, git_repo_url):
        self.git_repo_url = git_repo_url


class Progress(RemoteProgress):
    def update(self, *args):
        self.callback_func(self)


class AnsibleRepoEncoder(JSONEncoder):
    def default(self, o):
        return {
            "name": o.name,
            "localDirectory": o.local_repo_path,
            "layout": o.get_layout(),
            "gitRepoUrl": o.git_repo_url,
            "gitBranch": o.git_branch,
            "inventories": json.loads(json.dumps(o.inventories, cls=AnsibleInventoryEncoder)),
            "playbooks": json.loads(json.dumps(o.playbooks, cls=AnsilePlaybookEncoder)),
            "roles": json.loads(json.dumps(o.roles, cls=AnsibleRoleEncoder))
        }


class AnsibleRepo(object):
    def __init__(self):
        """
        Initialize an AnsibleRepo object.

        :return: The instance
        """
        self._log_path = '/etc/ansible-townhall/logs/'

        self._regex = '(\w+://)(.+@)*([\w\d\.]+)(:[\d]+){0,1}/*(.*/(.*)\.git)'

        self.name = None

        self.local_repo_path = None

        self.git_repo_url = None
        self.git_branch = None

        self._git_repo_obj = None

        self._layout = None

        self.roles = None
        self.playbooks = None
        self.inventories = None

    def load_from_json(self, json_data):
        """
        Rebuild the object from json

        :param json_data:
        :return:
        """
        self.name = json_data['name']
        self.local_repo_path = json_data['localDirectory']
        self.git_repo_url = json_data['gitRepoUrl']
        self.git_branch = json_data['gitBranch']
        self._layout = json_data['layout']
        self._git_repo_obj = Repo(self.local_repo_path)

    def load_from_local(self, local_repo_path, layout):
        self.name = local_repo_path.rstrip('/').split('/')[-1]
        self.local_repo_path = local_repo_path
        self._layout = layout
        self._git_repo_obj = Repo(local_repo_path)
        self.git_repo_url = self._git_repo_obj.remote().config_reader.get('url')
        self.git_branch = self._git_repo_obj.active_branch.name

    def load_from_git(self, git_repo_url, layout, git_branch='master', local_base_path='/etc/ansible-townhall/repos/'):
        """
        Clone the specified code repo to local store and generate metadata for it.

        :param git_repo_url: The URL of the git repo
        :param git_branch: The git branch to clone
        :param local_base_path: The local base path to clone the git repo to
        :return: True if everything is OK.
        """
        self.git_repo_url = git_repo_url

        if git_branch:
            self.git_branch = git_branch
        else:
            self.git_branch = 'master'

        self._layout = layout

        self.name = self._get_repo_name(self.git_repo_url)
        if not local_base_path:
            local_base_path = '/etc/ansible-townhall/repos/'
        self.local_repo_path = ''.join([local_base_path, self.name])

        self._create_repo_directory(self.local_repo_path)

        # def write_gitprogress(progress):
        #     with open(''.join([self._log_path, 'gitlog.', self.name]), 'a') as f:
        #         f.write(progress._cur_line + '\n')

        #progress = Progress(write_gitprogress)

        self._git_repo_obj = Repo.clone_from(self.git_repo_url, self.local_repo_path, branch=self.git_branch,
                                             progress=None)

    def get_layout(self):
        return self._layout

    def generate_metadata(self):
        """
        Generate the metadata for the repo against a specified layout.

        :param layout: A JSON dict to specify the layout of the Ansible repo
        :return: The metadata
        """
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
                inv_path = ''.join([self.local_repo_path, layout['root'], filename])
                inventories[filename] = AnsibleInventory(filename,inv_path)
            return inventories

    def _process_playbooks(self, layout):
        playbooks = dict()
        if 'playbooks' not in layout:
            return None
        pattern_type = layout['playbooks']['type']
        if pattern_type == 'regex':
            playbooks_dir = ''.join([self.local_repo_path, layout['root']])
            for item in os.listdir(playbooks_dir):
                playbook_path = ''.join([playbooks_dir, item])
                if os.path.isfile(playbook_path) and re.match(layout['playbooks']['pattern'], item):
                    key = item.split('.')[0]
                    playbooks[key] = AnsiblePlaybook(key, playbook_path)

            return playbooks

    def _process_roles(self, layout):
        roles = dict()
        if 'roles' not in layout:
            return None
        pattern_type = layout['roles']['type']
        if pattern_type == 'dirnames':
            for dir_role in layout['roles']['pattern'].split(','):
                roles_dir = ''.join([self.local_repo_path, layout['root'], dir_role])
                for directory in os.listdir(roles_dir):
                    role = AnsibleRole(''.join([roles_dir, directory]))
                    roles[role.name] = role
            return roles

    @staticmethod
    def _create_repo_directory(local_repo_path):
        if os.path.exists(local_repo_path):
            shutil.rmtree(local_repo_path)
        os.makedirs(local_repo_path)

    def _get_repo_name(self, git_repo_url):
        m = re.match(self._regex, git_repo_url)
        if m:
            return m.groups()[-1]
        else:
            raise InvalidGitRepoUrlException(git_repo_url)
