from . import ui
from flask import render_template


@ui.route('/ui')
def ui():
    return render_template('template_index.html')
