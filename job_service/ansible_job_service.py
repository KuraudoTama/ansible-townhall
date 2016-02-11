from multiprocessing import Pool
import pexpect
import os
from job_exception.ansible_job_exception import RecordNotFoundException
from job_logging.ansible_job_logger import logger
from job_persistence.ansible_job_db import job_DAO

LOG_OUTPUT_RELATIVE_DIR = "/job_logging/log_output"


def _create_log_output_file_path(job_id):
    current_file_realpath = os.path.realpath(__file__)
    current_file_dir = os.path.dirname(current_file_realpath)
    project_root_dir = os.path.dirname(current_file_dir)

    log_output_file_dir_realpath = project_root_dir + LOG_OUTPUT_RELATIVE_DIR
    if not os.path.exists(log_output_file_dir_realpath):
        os.mkdir(log_output_file_dir_realpath)

    log_output_file = "/%s.log" % job_id
    log_output_file_realpath = log_output_file_dir_realpath + log_output_file
    logger.info("log output file real path is: %s" % log_output_file_realpath)
    return log_output_file_realpath


def launch_ansible_playbook_command(ansible_command, job_id, password=None, become_password=None):
    logger.info("Enter")
    log_output_file_realpath = _create_log_output_file_path(job_id)
    output_file = open(log_output_file_realpath, 'a')
    try:
        if password and become_password:
            password_str = password + "\n"
            become_password_str = become_password + "\n"
            logger.info(pexpect.run(ansible_command, logfile=output_file, timeout=-1,
                                    events={"SSH password:": password_str, "SUDO password.*:": become_password_str}))
        elif password:
            password_str = password + "\n"
            logger.info(
                pexpect.run(ansible_command, logfile=output_file, timeout=-1, events={"SSH password:": password_str}))
        elif become_password:
            become_password_str = become_password + "\n"
            logger.info(pexpect.run(ansible_command, logfile=output_file, timeout=-1,
                                    events={".*password:": become_password_str}))
        else:
            logger.info(pexpect.run(ansible_command, logfile=output_file, timeout=-1))
    finally:
        if output_file:
            output_file.close()

    logger.info("Exit")


class JobService(object):
    def __init__(self):
        self.process_pool = Pool()

    def get_job_list(self, page_index, page_size):
        return job_DAO.get_job_list(page_index, page_size)

    def get_job_details(self, job_id, projection_dict=None):
        job_doc = None
        try:
            job_doc = job_DAO.get_job_details(job_id, projection_dict)
        except RecordNotFoundException:
            raise

        return job_doc

    def create_job(self, job):
        job["status"] = "New"
        return job_DAO.create_job(job)

    def __make_ansible_command_str(self, job_doc):
        logger.info("Enter")
        command_separator = " "
        command_list = []
        command_list.append("/usr/bin/ansible-playbook")
        password = None
        become_password = None

        inventory_file = job_doc.get("inventory")
        playbook_file = job_doc.get("playbook")
        forks = job_doc.get("forks")
        job_id = str(job_doc.get("_id"))

        credentials = job_doc.get("credentials", None)
        if credentials:
            username = credentials.get("username", None)
            if username:
                command_list.append("--user=%s" % username)

            private_key_file = credentials.get("private_key_file", None)
            if private_key_file:
                command_list.append("--private-key=%s" % private_key_file)

            password = credentials.get("password", None)
            if password:
                command_list.append("--ask-pass")

            become_method = credentials.get("become_method", None)
            if become_method:
                command_list.append("--become-method=%s" % become_method)

            become_user = credentials.get("become_user", None)
            if become_user:
                command_list.append("--become-user=%s" % become_user)

            become_password = credentials.get("become_password", None)
            if become_password:
                command_list.append("--ask-become-pass")

        command_list.append("--inventory-file=%s" % inventory_file)
        command_list.append("-e job_id=%s" % job_id)
        if forks:
            command_list.append("--forks=%d" % forks)
        command_list.append(playbook_file)

        command_str = command_separator.join(command_list)

        logger.info("The ansible command is:%s" % command_str)
        logger.info("Exit")

        return command_str, password, become_password

    def launch_job(self, job_id):
        job_doc = self.get_job_details(job_id)

        ansible_command, password, become_password = self.__make_ansible_command_str(job_doc)
        self.process_pool.apply_async(func=launch_ansible_playbook_command,
                                      args=(ansible_command, job_id, password, become_password))

    def get_total_counts_grouped_by_categories(self, job_id):
        return job_DAO.get_total_counts_grouped_by_categories(job_id)

    def get_task_duration_grouped_by_names(self, job_id, size):
        return job_DAO.get_task_duration_grouped_by_names(job_id, size)

    def access_codebase(self):
        pass

    def __encrypt_password(self, plain_password):
        pass

    def __decrypt_password(self, encrypted_password):
        pass

    def get_logs_output(self, job_id, read_size):
        logger.info("Enter")
        logger.info("log output file's read size is: %u" % read_size)

        log_output_file_realpath = _create_log_output_file_path(job_id)
        log_output_dict = {}
        if os.path.exists(log_output_file_realpath):
            output_file_object = open(log_output_file_realpath, 'r')
            job_doc = job_DAO.get_job_details(job_id, {"_id": False, "status": True})
            job_status = job_doc["status"]
            logger.info("Current job status is:%s" % job_status)
            current_file_size = os.path.getsize(log_output_file_realpath)
            logger.info("Current log output file's size snapshot is:%u" % current_file_size)
            unread_size = current_file_size - read_size
            logger.info("Current log output file's unread size is:%u" % unread_size)
            output_file_object.seek(read_size)
            log_content = output_file_object.read(unread_size)
            logger.info("Current log output file's content is:%s" % log_content)
            log_output_dict["read_size"] = current_file_size
            log_output_dict["job_status"] = job_status
            log_output_dict["current_log_content"] = log_content

        logger.info("Exit")
        return log_output_dict


job_service = JobService()
