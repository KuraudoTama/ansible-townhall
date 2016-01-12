import os
import time
import datetime
import json
from pymongo import MongoClient
from bson.objectid import ObjectId

DB_HOST = "127.0.0.1"
DB_PORT = 27017
DB_NAME = "ansible_job_dw"
LOG_COLLECTION_NAME = "ansible_log"
JOB_COLLECTION_NAME = "ansible_job"

ansible_db_connection = MongoClient(DB_HOST, DB_PORT)
ansible_db = ansible_db_connection[DB_NAME]
collection_name_list = ansible_db.collection_names(include_system_collections=False)

if LOG_COLLECTION_NAME not in collection_name_list:
    ansible_db.create_collection(LOG_COLLECTION_NAME, size=1*1024*1024*1024, capped=True)

log_collection = ansible_db[LOG_COLLECTION_NAME]
job_collection = ansible_db[JOB_COLLECTION_NAME]


class CallbackModule(object):

    TIME_FORMAT="%b %d %Y %H:%M:%S"
    
    
    def __init__(self):
        # For storing timings
        self.stats = {}
        # For storing the name of the current task
        self.current = None

    def log(self, host, category, data):
            if self.current is not None:
                duration = self.stats[self.current] = time.time() - self.stats[self.current]
                
            if '_ansible_verbose_override' in data:
                # avoid logging extraneous data
                data = 'omitted'
            else:
                data = data.copy()
                data = json.dumps(data)
                
                if str(data).find("verbose_override") != -1:
                    data="omitted as setup log"
                else:
                    print "----------------------------------------------------------------------------------"
                    print data
                    print "----------------------------------------------------------------------------------"
                    now = time.strftime(self.TIME_FORMAT, time.localtime())
#                     ansible_job_dict = self.play.playbook.extra_vars
#                     ansible_job_id = ansible_job_dict.get("job_id")
                    log_collection.insert_one(dict(now=now, node_IP = host, task_name = self.current, category=category, task_duration = duration, job_id=self.ansible_job_id,data=data))
                   

    def on_any(self, *args, **kwargs):
        pass

    def runner_on_failed(self, host, res, ignore_errors=False):
        #human_log(res)
        self.log(host,"FAILED",res)
    def runner_on_ok(self, host, res):
        #human_log(res)
        self.log(host,"OK",res)
    def runner_on_error(self, host, msg):
        pass
    
    def runner_on_skipped(self, host, item=None):
        pass

    def runner_on_unreachable(self, host, res):
        self.log(host,"UNREACHABLE",res)
    
    def runner_on_no_hosts(self):
        pass
    
    def runner_on_async_poll(self, host, res, jid, clock):
        pass

    def runner_on_async_ok(self, host, res, jid):
        pass

    def runner_on_async_failed(self, host, res, jid):
        pass
    
    def __update_job_status(self, job_id, job_status):
        job_collection.update_one({"_id" : ObjectId(job_id)},
                                  {"$set" : {"status" : job_status}} 
                                  )
    
    def playbook_on_start(self):
        ansible_job_dict = self.playbook.extra_vars
        self.ansible_job_id = ansible_job_dict.get("job_id")
        self.__update_job_status(self.ansible_job_id, "Executing")
        print "Get job id on playbook start:", self.ansible_job_id
    
    def playbook_on_notify(self, host, handler):
        pass
    
    def playbook_on_no_hosts_matched(self):
        pass
    
    def playbook_on_no_hosts_remaining(self):
        pass

    def playbook_on_task_start(self, name, is_conditional):
        """
        Logs the start of each task
        """
        self.current = name
        # Record the start time of the current task
        self.stats[self.current] = time.time()
        
    def playbook_on_vars_prompt(self, varname, private=True, prompt=None, encrypt=None, confirm=False, salt_size=None, salt=None, default=None):
        pass
    
    def playbook_on_setup(self):
        pass
    
    def playbook_on_import_for_host(self, host, imported_file):
        pass
    
    def playbook_on_not_import_for_host(self, host, missing_file):
        pass
    
    def playbook_on_play_start(self, pattern):
        pass

    def playbook_on_stats(self, stats):
        count = log_collection.find({"$or" : [{"job_id":self.ansible_job_id, "category":"FAILED"}, {"job_id":self.ansible_job_id, "category":"UNREACHABLE"}]}).count()
        print "Failure count:", count
        if count > 0:
            self.__update_job_status(self.ansible_job_id, "Failure")
        else:
            self.__update_job_status(self.ansible_job_id, "Success")
