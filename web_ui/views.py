from . import ui
from flask import render_template


@ui.route('/ui')
def ui_index():
    return render_template('template_index.html')


@ui.route('/ui/jobs/create')
def ui_create_jobs():
    return render_template('template_job_create.html')