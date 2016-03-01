import json
from flask import request, Response
from flask.ext.cors import CORS, cross_origin
from . import inventory_api
from job_logging.ansible_job_logger import logger


common_header = {'Content-Type': 'text/json', 'Access-Control-Allow-Origin': '*'}


@inventory_api.route("/api/inventories", methods=['GET', 'POST'])
@cross_origin(origin='*')
def inventory_collection():
    """
    The POST data should be in this format:

    {
      "name": <inventory name>,
      "content": <inventory content>
    }

    :return:

    {
      "name": <inventory name>,
      "content": <inventory content>,
      "path": <inventory path on the server>,
      "message": "created"
    }
    """
    try:
        if request.method == 'GET':
            return Response('{ "msg":"hello"}', mimetype='application/json')
    except Exception, e:
        logger.error("Error %s" % str(e), exc_info=True)
        return Response('error', mimetype='application/json')
