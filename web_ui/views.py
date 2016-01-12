from . import ui


@ui.route('/ui')
def ui():
    return 'hello ansible'
