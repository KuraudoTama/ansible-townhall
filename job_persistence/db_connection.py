from pymongo import MongoClient

DB_HOST = "mongo" #"127.0.0.1"
DB_PORT = 27017
DB_NAME = "ansible_job_dw"

job_db_connection = MongoClient(DB_HOST, DB_PORT)
job_db = job_db_connection[DB_NAME]
