from flask import Flask

import common.settings as settings
from code_repo_api import repo_api
from inventory_api import inventory_api
from job_api import api
from service_status_api import status_api
from web_ui import ui


if __name__ == '__main__':
    app = Flask(__name__)
    app.register_blueprint(ui)
    app.register_blueprint(api)
    app.register_blueprint(repo_api)
    app.register_blueprint(inventory_api)
    app.register_blueprint(status_api)
    app.run(host=settings.get_app_host(), port=settings.get_app_port(), debug=settings.get_debug_flag())
