from bson.objectid import ObjectId

from db_connection import job_db
from job_exception.ansible_job_exception import RecordNotFoundException
from job_logging.ansible_job_logger import logger


class JobPersistence(object):
    def __init__(self):
        self.job_collection = job_db["ansible_job"]

    def get_job_list(self, page_index, page_size):
        skip_item = (page_index - 1) * page_size
        results = self.job_collection.find(skip=skip_item, limit=page_size)
        job_list = []
        job_list_dict = {}
        for job in results:
            job["_id"] = str(job.get("_id"))
            job_list.append(job)
            logger.info("Appending to job_list:%s" % str(job))

        logger.info("Job list size is:%d" % len(job_list))
        job_list_dict["job_list"] = job_list
        return job_list_dict

    def get_job_details(self, job_id, projection_dict=None):
        job_doc = self.job_collection.find_one({"_id": ObjectId(job_id)}, projection=projection_dict)
        if not job_doc:
            raise RecordNotFoundException("Record is not found by the job id '%s'" % job_id)

        job_doc["_id"] = str(job_doc.get("_id"))
        logger.info("Job is:%s" % job_doc)
        return job_doc

    def create_job(self, job):
        inserted_doc_dict = {}
        inserted_doc = self.job_collection.insert_one(job)
        inserted_doc_dict["_id"] = str(inserted_doc.inserted_id)
        return inserted_doc_dict

    def update_job_status(self, job_id, job_status):
        self.job_collection.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {"status": job_status}}
        )


job_DAO = JobPersistence()
