import os
from pymongo import MongoClient

DB_NAME = "ansible_job_dw"

job_db_connection = MongoClient(os.environ['MONGO_URL'])
job_db = job_db_connection[DB_NAME]
