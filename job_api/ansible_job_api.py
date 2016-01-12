from job_service.ansible_job_service import job_service
from job_logging.ansible_job_logger import logger
from job_exception.ansible_job_exception import InvalidContentTypeException
from job_exception.ansible_job_exception import MissingKeyException
from job_exception.ansible_job_exception import MissingDataException
from job_exception.ansible_job_exception import InvalidDataTypeException
from job_exception.ansible_job_exception import InvalidDataException
from job_exception.ansible_job_exception import RecordNotFoundException
from flask import Flask
from flask import request
from flask import json
from flask import make_response
from werkzeug.exceptions import BadRequest
from . import api

#app = Flask("ansible-job")


def _check_content_type(required_content_type):
    index = request.headers["Content-Type"].find(required_content_type)
    if index == -1:
        raise InvalidContentTypeException("Please change the value of 'Content-Type' to '%s'." % required_content_type)


def _make_error_response(status_code, error_message):
    logger.error("Error Code:%s-%s" % (status_code, error_message), exc_info=True)
    returned_error_dict = {"error_message": error_message}
    return make_response(json.jsonify(returned_error_dict), status_code)


@api.route("/api/v1/ansible-job/job-list", methods=["POST"])
def get_job_list():
    logger.info("Enter")
    response = None
    try:
        _check_content_type("application/json")
        logger.info("Request Parameters : %s" % request.data)
        request_parameters = request.get_json()
        if not isinstance(request_parameters, dict) or not request_parameters:
            raise BadRequest

        page_index = request_parameters.get("page_index", None)
        page_size = request_parameters.get("page_size", None)

        if (page_index is None) or (page_size is None):
            raise MissingKeyException("Both 'page_index' and 'page_size' keys are required in the json request body.")

        if (not isinstance(page_index, int)) or (not isinstance(page_size, int)):
            raise InvalidDataTypeException("The values of 'page_index' and 'page_size' must be integer.")

        if (page_index < 1) or (page_size < 1):
            raise InvalidDataException(
                "Both the values of 'page_index' and 'page_size' must be greater than or equal to 1.")

        job_list = job_service.get_job_list(page_index, page_size)
        response = make_response(json.jsonify(job_list), 200)

    except InvalidContentTypeException, e:
        response = _make_error_response(415, str(e))
    except BadRequest, e:
        error_message = "Invalid json request body.Please follow the format {'page_index':your_value, 'page_size':your_value}"
        response = _make_error_response(400, error_message)
    except (MissingKeyException, InvalidDataTypeException, InvalidDataException), e:
        response = _make_error_response(400, str(e))
    except Exception, e:
        response = _make_error_response(500, str(e))

    logger.info("Exit")
    return response


@api.route("/api/v1/ansible-job/codebase")
def access_codebase():
    pass


@api.route("/api/v1/ansible-job/job", methods=["POST"])
def create_job():
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


@api.route("/api/v1/ansible-job/job-status/<job_id>")
def get_job_status(job_id):
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


@api.route("/api/v1/ansible-job/job/<job_id>")
def get_job_details(job_id):
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


# if __name__ == "__main__":
#     app.run(host='0.0.0.0')
