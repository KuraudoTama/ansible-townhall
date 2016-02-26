from flask import Flask
from web_ui import ui
from job_api import api
from code_repo_api import repo_api


app = Flask(__name__)
app.register_blueprint(ui)
app.register_blueprint(api)
app.register_blueprint(repo_api)
app.run(host='0.0.0.0', port=8080, debug=True)
