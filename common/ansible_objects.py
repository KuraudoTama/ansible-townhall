from json import JSONEncoder


class AnsibleInventory(object):
    def __init__(self, name, inv_path):
        self.name = name
        self._inv_path = inv_path

    def path(self):
        return self._inv_path


class AnsibleInventoryEncoder(JSONEncoder):
    def default(self, o):
        return {
            "name": o.name,
            "path": o.path()
        }


class AnsibleVars(object):
    pass


class AnsibleLibrary(object):
    pass


class AnsiblePlugin(object):
    pass


class AnsiblePlaybook(object):
    def __init__(self, name, book_path):
        self.name = name
        self._book_path = book_path

    def path(self):
        return self._book_path


class AnsilePlaybookEncoder(JSONEncoder):
    def default(self, o):
        return {
            "name": o.name,
            "path": o.path()
        }


class AnsibleRole(object):
    def __init__(self, role_dir):
        self._dir = role_dir
        self.name = role_dir.rstrip('/').split('/')[-1]

    def path(self):
        return self._dir

    def _parse_dir(self):
        pass

    def get_content(self):
        pass


class AnsibleRoleEncoder(JSONEncoder):
    def default(self, o):
        return {
            "name": o.name,
            "path": o.path()
        }
