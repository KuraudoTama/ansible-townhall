from flask import json
from flask import make_response
from flask import request
from werkzeug.exceptions import BadRequest

from job_exception.ansible_job_exception import InvalidContentTypeException
from job_exception.ansible_job_exception import InvalidDataException
from job_exception.ansible_job_exception import InvalidDataTypeException
from job_exception.ansible_job_exception import MissingDataException
from job_exception.ansible_job_exception import MissingKeyException
from job_exception.ansible_job_exception import RecordNotFoundException
from job_logging.ansible_job_logger import logger
from job_service.ansible_job_service import job_service
from . import api


def _check_content_type(required_content_type):
    index = request.headers["Content-Type"].find(required_content_type)
    if index == -1:
        raise InvalidContentTypeException("Please change the value of 'Content-Type' to '%s'." % required_content_type)


def _make_error_response(status_code, error_message):
    logger.error("Error Code:%s-%s" % (status_code, error_message), exc_info=True)
    returned_error_dict = {"error_message": error_message}
    return make_response(json.jsonify(returned_error_dict), status_code)


@api.route("/jobs")
def get_job_list():
    '''
    Get the job list from the DB
    To call this API, the form is:
    http://<host>:<port>/jobs?page_index=<positive integer>&page_size=<positive integer>
    Method: Get
    
    Both query parameters 'page_index' and 'page_size' must be given and they are positive integers.
    '''
    logger.info("Enter")
    response = None
    try:
        page_index = request.args.get("page_index", None)
        page_size = request.args.get("page_size", None)
        
        logger.info("page_index is : %s" % page_index)
        logger.info("page_size is : %s" % page_size)

        if (page_index is None) or (page_size is None):
            raise MissingKeyException("Both 'page_index' and 'page_size' keys are required.")

        if (not page_index.isdigit()) or (not page_size.isdigit()):
            raise InvalidDataTypeException("The values of 'page_index' and 'page_size' must be positive integer.")
        else:
            page_index = int(page_index)
            page_size = int(page_size)

        if (page_index < 1) or (page_size < 1):
            raise InvalidDataException(
                "Both the values of 'page_index' and 'page_size' must be greater than or equal to 1.")

        job_list = job_service.get_job_list(page_index, page_size)
        response = make_response(json.jsonify(job_list), 200)
        
    except (MissingKeyException, InvalidDataTypeException, InvalidDataException), e:
        response = _make_error_response(400, str(e))
    except Exception, e:
        response = _make_error_response(500, str(e))

    logger.info("Exit")
    return response


#@api.route("/api/v1/ansible-job/codebase")
#def access_codebase():
    #pass


@api.route("/jobs", methods=["POST"])
def create_job():
    '''
    Store a job and launch it. After launching the job, this api returns immediately with a new job id in response.
    Meanwhile, the job executes in the backend asynchronously.
    To call this API, the form is:
    http://<host>:<port>/jobs
    Method: POST
    Content-Type: application/json
    
    In request body:
    'job_name', 'inventory_path' and 'playbook_path' must be given.
    'job_description', 'forks' and 'credentials' block are optional.
    
    In 'credentials' block:
    if 'username' is given, either 'password' or 'private_key_file' must be given.
    if 'password' or 'private_key_file' is not empty, the corresponding 'username' must be given.
    'become_method' is optional.
    if 'become_user' is given, the 'become_password' must be provided, vice versa.
    
    Request body Example:
    {
        "name" : "test job 1",
        "description" : "test job 1 description.",
        "inventory" : "/etc/ansible/hosts",
        "playbook" : "/root/ansible_log_test/ansible_test.yml",
        "forks" : 5,
        "credentials" : {
            "username" : "root",
            "password" : "MbvG6Nw8",
            "become_password" : "MbvG6Nw8",
            "become_user" : "root"
            }
    }
    '''
    logger.info("Enter")
    response = None
    try:
        _check_content_type("application/json")
        logger.info("Request Parameters : %s" % request.data)
        request_parameters = request.get_json()
        if not isinstance(request_parameters, dict) or not request_parameters:
            raise BadRequest

        job_name = request_parameters.get("name", None)
        if job_name is None:
            raise MissingKeyException("The job's 'name' is required.")
        if not isinstance(job_name, basestring):
            raise InvalidDataTypeException("The job's 'name' must be 'String' type.")
        if not job_name:
            raise InvalidDataException("The job's 'name' must not be empty.")

        job_description = request_parameters.get("description", None)
        if job_description is not None:
            if not isinstance(job_description, basestring):
                raise InvalidDataTypeException("The job's 'description' must be 'String' type.")

        inventory_path = request_parameters.get("inventory", None)
        if inventory_path is None:
            raise MissingKeyException("The job's 'inventory' is required.")
        if not isinstance(inventory_path, basestring):
            raise InvalidDataTypeException("The job's 'inventory' must be 'String' type.")
        if not inventory_path:
            raise InvalidDataException("The job's 'inventory' must not be empty.")

        playbook_path = request_parameters.get("playbook", None)
        if playbook_path is None:
            raise MissingKeyException("The job's 'playbook' is required.")
        if not isinstance(playbook_path, basestring):
            raise InvalidDataTypeException("The job's 'playbook' must be 'String' type.")
        yml_index = playbook_path.find('.yml')
        if (not playbook_path) or (yml_index == -1):
            raise InvalidDataException(
                "The job's 'playbook' must not be empty and must be a valid YAML file path like '<your_path>/test.yml'.")

        credentials = request_parameters.get("credentials", None)
        if credentials is not None:
            if not isinstance(credentials, dict):
                raise InvalidDataTypeException("The job's 'credentials' must be 'Object' or 'Dictionary' type.")
            else:
                username = credentials.get("username", None)
                password = credentials.get("password", None)
                private_key_file = credentials.get("private_key_file", None)
                if username is not None:
                    if not isinstance(username, basestring):
                        raise InvalidDataTypeException("The 'username' must be 'String' type.")
                    if not username:
                        raise InvalidDataException("The 'username' must not be empty string.")
                    if (password is None) and (private_key_file is None):
                        raise MissingKeyException(
                            "Please provide either 'password' or 'private_key_file' corresponding to the 'username' : %s" % username)
                    else:
                        if password is not None:
                            if not isinstance(password, basestring):
                                raise InvalidDataTypeException("The 'password' must be 'String' type.")
                            if not password:
                                raise InvalidDataException("The 'password' must not be empty string.")
                        if private_key_file is not None:
                            if not isinstance(private_key_file, basestring):
                                raise InvalidDataTypeException("The 'private_key_file' must be 'String' type.")
                            if not private_key_file:
                                raise InvalidDataException("The 'private_key_file' must not be empty string.")
                else:
                    if (password is not None) or (private_key_file is not None):
                        raise MissingKeyException(
                            "please provide 'username' corresponding to the 'password' or 'private_key_file'")

                become_method = credentials.get("become_method", None)
                become_user = credentials.get("become_user", None)
                become_password = credentials.get("become_password", None)

                if become_method is not None:
                    if not isinstance(become_method, basestring):
                        raise InvalidDataTypeException("The 'become_method' must be 'String' type.")
                    if not become_method:
                        raise InvalidDataException("The 'become_method' must not be empty string.")

                if become_user is not None:
                    if not isinstance(become_user, basestring):
                        raise InvalidDataTypeException("The 'become_user' must be 'String' type.")
                    if not become_user:
                        raise InvalidDataException("The 'become_user' must not be empty string.")
                    if become_password is None:
                        raise MissingKeyException(
                            "Please provide the 'become_password' corresponding to the 'become_user' : %s" % become_user)
                    else:
                        if not isinstance(become_password, basestring):
                            raise InvalidDataTypeException("The 'become_password' must be 'String' type.")
                        if not become_password:
                            raise InvalidDataException("The 'become_password' must not be empty string.")
                else:
                    if become_password is not None:
                        raise MissingKeyException(
                            "Please provide the 'become_user' corresponding to the 'become_password'.")

        forks = request_parameters.get("forks", None)
        if forks is not None:
            if not isinstance(forks, int):
                raise InvalidDataTypeException("The 'forks' must be integer.")
            if (forks < 5):
                raise InvalidDataException("The 'forks' number must be greater than or equal to 5.")

        job_dict = job_service.create_job(request_parameters)
        job_service.launch_job(job_dict["_id"])
        response = make_response(json.jsonify(job_dict), 201)
    except InvalidContentTypeException, e:
        response = _make_error_response(415, str(e))
    except BadRequest, e:
        error_message = "Invalid json request body."
        response = _make_error_response(400, error_message)
    except (MissingKeyException, InvalidDataTypeException, InvalidDataException), e:
        response = _make_error_response(400, str(e))
    except Exception, e:
        response = _make_error_response(500, str(e))
    logger.info("Exit")
    return response


@api.route("/jobs/job-status/<job_id>")
def get_job_status(job_id):
    '''
    Retrieve the job status.
    The client should periodically call this api to get the latest job status.
    Job status includes: 'New', 'Executing', 'Failure' and 'Success'.
    To call this API, the form is:
    http://<host>:<port>/jobs/job-status/<job_id>
    Method: Get
    
    It returns a 'status' corresponding to above job_id.
    '''
    logger.info("Enter")
    response = None
    try:
        if not job_id:
            raise MissingDataException("Missing 'job_id'.")

        job_doc = job_service.get_job_details(job_id, {"_id": True, "status": True})
        response = make_response(json.jsonify(job_doc))
    except (MissingDataException, RecordNotFoundException), e:
        response = _make_error_response(404, str(e))
    except Exception, e:
        response = _make_error_response(500, str(e))

    logger.info("Exit")
    return response


@api.route("/jobs/<job_id>")
def get_job_details(job_id):
    '''
    Retrieve the job details.
    To call this API, the form is:
    http://<host>:<port>/jobs/<job_id>
    Method: Get
    '''
    logger.info("Enter")
    response = None
    try:
        if not job_id:
            raise MissingDataException("Missing 'job_id'.")

        job_doc = job_service.get_job_details(job_id)
        response = make_response(json.jsonify(job_doc), 200)
    except (MissingDataException, RecordNotFoundException), e:
        response = _make_error_response(404, str(e))
    except Exception, e:
        response = _make_error_response(500, str(e))

    logger.info("Exit")
    return response


@api.route("/logs/total-counts-grouped-by-categories/<job_id>")
def get_total_counts_grouped_by_categories(job_id): 
    '''
    Get the total counts of ansible task logs that are associated with 'job_id' and grouped by categories.
    The categories of ansible task are 'FAILED', 'OK' and 'UNREACHABLE'.
    This API intends to be used by client for drawing the chart. 
    
    To call this API, the form is:
    http://<host>:<port>/logs/total-counts-grouped-by-categories/<job_id>
    Method: Get
    
    Response body example:
    {
        'FAILED' : 2,
        'OK' : 10,
        'UNREACHABLE' : 0
    }
    '''
    logger.info("Enter")
    response = None
    try:
        count_dict = job_service.get_total_counts_grouped_by_categories(job_id)
        response = make_response(json.jsonify(count_dict), 200)
    except RecordNotFoundException, e:
        response = _make_error_response(404, str(e))
    except Exception, e:
        response = _make_error_response(500, str(e))
        
    logger.info("Exit")
    return response

@api.route("/logs/task-duration-grouped-by-names/<job_id>")
def get_task_duration_grouped_by_names(job_id): 
    '''
    Get each task duration which is associated with 'job_id' and grouped by task names.
    A task in playbook could be executed multiple times, so the task duration is an accumulated value.
    The value of the duration is seconds.
    This API intends to be used by client for drawing the chart. 
    
    To call this API, the form is:
    http://<host>:<port>/logs/task-duration-grouped-by-names/<job_id>
    Method: Get
    
    Response body example:
    {
        task_duration_list:[
            {'Install MongoDB' : 1.55555555},
            {'Show print message' : 0.00111}
        ]
    }
    '''
    logger.info("Enter")
    response = None
    try:
        size = request.args.get("size", None)
        logger.info("size is : %s" % size)
        if size is None:
            raise MissingKeyException("The 'size' field is required.")
        if not size.isdigit():
            raise InvalidDataTypeException("The 'size' must be positive integer.")
        else:
            size = int(size)
            
        if size <= 0:
            raise InvalidDataException("The 'size' must be greater than 0.")
        
        task_dict = job_service.get_task_duration_grouped_by_names(job_id, size)
        response = make_response(json.jsonify(task_dict), 200)
        
    except (MissingKeyException, InvalidDataTypeException, InvalidDataException), e:
        response = _make_error_response(400, str(e))
    except Exception, e:
        response = _make_error_response(500, str(e))
    logger.info("Exit")
    return response

