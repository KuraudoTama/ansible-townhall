import os


def get_log_file_path():
    return os.environ.get('LOGFILE', '/etc/ansible-townhall/ansible-townhall.log')


def get_mongodb_url():
    return os.environ.get('MONGO_URL', 'mongodb://localhost:27017')


def get_app_port():
    return os.environ.get('APP_PORT', 8080)


def get_app_host():
    return os.environ.get('APP_HOST', '0.0.0.0')


def get_debug_flag():
    return os.environ.get('DEBUG', False)
