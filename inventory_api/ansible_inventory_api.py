from flask import request, Response
from flask.ext.cors import cross_origin

from common.ansible_townhall_logger import logger
from . import inventory_api

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
            logger.info('hi')
            return Response('{ "msg":"hello"}', mimetype='application/json')
    except Exception, e:
        logger.error("Error %s" % str(e), exc_info=True)
        return Response('error', mimetype='application/json')
