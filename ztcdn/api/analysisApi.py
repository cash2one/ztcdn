# -*- coding: utf-8 -*-
__author__ = 'liujiahua'
from flask import jsonify
from flask import request
from ztcdn.api import cdn_api
from ztcdn.util.apiUtil import verifyUrl, getUserProjByToken, get_cdn_log
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


@cdn_api.route('/analysis', methods=['GET'])
def analysis():
    if not request.json:
        return jsonify({"error": "Bad request, no json data"}), 400
    domain_name = request.json.get("domainName")
    start = request.json.get("start")
    end = request.json.get("end")
    if not domain_name or not start or not end:
        return jsonify({"error": "Bad request, please check request data"}), 400

    # 验证是不是自己的域名
    project_ids = []
    token = request.headers.get("X-Auth-Token")
    project_id = request.json.get("project_id")
    if project_id:
        project_ids = [project_id]
    else:
        user = getUserProjByToken(token)
        project_dict = user.proj_list
        for keys in project_dict:
            project_ids.append(keys)
    verify_result = verifyUrl(domain_name, project_ids)
    if verify_result.has_key("error"):
        return jsonify(verify_result), 403
    res = get_cdn_log(domain_name, start, end)
    return jsonify(res)