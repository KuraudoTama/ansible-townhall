import json
import time
import pprint

from bson.objectid import ObjectId
from job_persistence.ansible_job_db import job_DAO


class CallbackModule(object):
    TIME_FORMAT = "%b %d %Y %H:%M:%S"

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
                data = "omitted as setup log"
            else:
                print "----------------------------------------------------------------------------------"
                print data
                print "----------------------------------------------------------------------------------"
                now = time.strftime(self.TIME_FORMAT, time.localtime())
                job_DAO.create_log(
                                   dict(now=now, 
                                        node_IP=host, 
                                        task_name=self.current, 
                                        category=category, 
                                        task_duration=duration,
                                        job_id=self.ansible_job_id, 
                                        data=data)
                                   )

    def on_any(self, *args, **kwargs):
        pass

    def runner_on_failed(self, host, res, ignore_errors=False):
        # human_log(res)
        self.log(host, "FAILED", res)

    def runner_on_ok(self, host, res):
        # human_log(res)
        self.log(host, "OK", res)

    def runner_on_error(self, host, msg):
        pass

    def runner_on_skipped(self, host, item=None):
        pass

    def runner_on_unreachable(self, host, res):
        self.log(host, "UNREACHABLE", res)

    def runner_on_no_hosts(self):
        pass

    def runner_on_async_poll(self, host, res, jid, clock):
        pass

    def runner_on_async_ok(self, host, res, jid):
        pass

    def runner_on_async_failed(self, host, res, jid):
        pass

    def playbook_on_start(self):
        ansible_job_dict = self.playbook.extra_vars
        ansible_playbook_name = self.playbook.filename
        print "Current playbook name is:", ansible_playbook_name
        self.ansible_job_id = ansible_job_dict.get("job_id")
        job_DAO.update_job_status(self.ansible_job_id, "Executing")
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

    def playbook_on_vars_prompt(self, varname, private=True, prompt=None, encrypt=None, confirm=False, salt_size=None,
                                salt=None, default=None):
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
        count = job_DAO.get_failed_logs_count(self.ansible_job_id)
        print "Failure count:", count
        if count > 0:
            job_DAO.update_job_status(self.ansible_job_id, "Failure")
        else:
            job_DAO.update_job_status(self.ansible_job_id, "Success")
        
        pprint.pprint(stats)
