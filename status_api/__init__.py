from flask import Blueprint

repo_api = Blueprint('repo_api', __name__)
import ansible_status_api
