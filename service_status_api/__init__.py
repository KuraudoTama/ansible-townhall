from flask import Blueprint

status_api = Blueprint('service_status_api', __name__)
import ansible_status_api
