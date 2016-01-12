from flask import Flask
from web_ui import ui
from job_api import api


app = Flask(__name__)
app.register_blueprint(ui)
app.register_blueprint(api)
app.run(debug=True)
