# -*- coding: utf-8 -*-
__author__ = 'liujiahua'
from flask import jsonify
from flask import request
from flask import abort
from ztcdn.api import cdn_api
from ztcdn.util.apiUtil import jsonToDomain, commonResult, addResult
import sys
from ztcdn.config import logging
reload(sys)
sys.setdefaultencoding('utf-8')

logger = logging.getLogger(__name__)

@cdn_api.route('/add', methods=['POST'])
def add():
    """
    从接收的 json 里生成 domain 对象
    """
    domain = jsonToDomain(request.json.get("domain"))
    project_id = request.json.get("projectId")
    username = request.json.get("username")
    result = addResult(domain, project_id, username)
    return result


@cdn_api.route('/find/<domain_id>', methods=['GET'])
def find(domain_id):
    result = commonResult('find', domain_id=domain_id)
    return result


@cdn_api.route('/modify', methods=['PUT'])
def modify():
    """
    domain 对象必须要指定 domainId 属性
    """
    if not request.json:
        abort(404)
    if not request.json.get("domain").get("domainId"):
        return jsonify({"error": "Can not find domainId"}), 404
    domain = jsonToDomain(request.json.get("domain"))
    result = commonResult('modify', domain=domain)
    return result


@cdn_api.route('/delete/<domain_id>', methods=['DELETE'])
def delete(domain_id):
    result = commonResult('delete', domain_id=domain_id)
    return result



