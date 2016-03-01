from flask import Blueprint

inventory_api = Blueprint('inventory_api', __name__)
import ansible_inventory_api
