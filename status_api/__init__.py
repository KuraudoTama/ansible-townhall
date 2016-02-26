from flask import Blueprint

status = Blueprint('status_api', __name__)
import ansible_status_api
