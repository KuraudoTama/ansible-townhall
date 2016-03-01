import os
import common.settings as settings
from pymongo import MongoClient

DB_NAME = "ansible_job_dw"

job_db_connection = MongoClient(settings.get_mongodb_url())
job_db = job_db_connection[DB_NAME]
