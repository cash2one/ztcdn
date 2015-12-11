# -*- coding: utf-8 -*-
__author__ = 'liujiahua'
from flask import jsonify
from flask import request
from ztcdn.api import cdn_api
from ztcdn.util.apiUtil import verifyUrl, mergeData, getUserProjByToken
import sys
from collections import OrderedDict

reload(sys)
sys.setdefaultencoding('utf-8')


@cdn_api.route('/flow', methods=['GET'])
def getFlow():
    if not request.json:
        return jsonify({"error": "Bad request, no json data"}), 400
    domain_names = request.json.get("domainName")
    start = request.json.get("start")
    end = request.json.get("end")
    if not domain_names or not start or not end:
        return jsonify({"error": "Bad request, please check request data"}), 400

    domain_names = domain_names.split(',')
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
    to_be_merged = []
    for domain_name in domain_names:
        verify_result = verifyUrl(domain_name, project_ids)
        if verify_result.has_key("error"):
            return jsonify(verify_result), 403
        else:
            cdn_clients = verify_result["cdn_clients"]

        all_cdn_len = len(cdn_clients)
        success_cdn = 0
        for i in cdn_clients:
            aaa = ''
            exec "import ztcdn.api." + i + ".api.domainApi as aaa"
            DomainApi = getattr(aaa, 'DomainApi')
            api = DomainApi()
            result = api.getFlowReport(domain_name, start, end)
            # res[i] = {}

            if result.getRet() == 0:
                success_cdn += 1
                if result.getFlowPoints():
                    item = OrderedDict()
                    for r in result.getFlowPoints():
                        item[r.point] = r.flow
                    # res[i]["flowValue"] = item
                    to_be_merged.append(item)
                    #res[i]["ret"] = 0
                    #res[i]["msg"] = 'OK'
                    #else:
                    #res[i] = {
                    #    "ret": result.getRet(),
                    #    "msg": result.getMsg(),
                    #}
    zt_flow_value = mergeData(to_be_merged)
    res = {"flowValue": zt_flow_value}
    return jsonify(res)


@cdn_api.route('/bandwidth', methods=['GET'])
def bandwidth():
    if not request.json:
        return jsonify({"error": "Bad request, no json data"}), 400
    domain_names = request.json.get("domainName")
    start = request.json.get("start")
    end = request.json.get("end")
    if not domain_names or not start or not end:
        return jsonify({"error": "Bad request, please check request data"}), 400

    domain_names = domain_names.split(',')
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
    to_be_merged = []
    for domain_name in domain_names:
        verify_result = verifyUrl(domain_name, project_ids)
        if verify_result.has_key("error"):
            return jsonify(verify_result), 403
        else:
            cdn_clients = verify_result["cdn_clients"]

        all_cdn_len = len(cdn_clients)
        success_cdn = 0
        for i in cdn_clients:
            aaa = ''
            exec "import ztcdn.api." + i + ".api.domainApi as aaa"
            DomainApi = getattr(aaa, 'DomainApi')
            api = DomainApi()
            result = api.getBandWidthReport(domain_name, start, end)
            # res[i] = {}

            if result.getRet() == 0:
                success_cdn += 1
                if result.getFlowPoints():
                    item = OrderedDict()
                    for r in result.getFlowPoints():
                        item[r.point] = r.flow
                    # res[i]["flowValue"] = item
                    to_be_merged.append(item)
                    #res[i]["ret"] = 0
                    #res[i]["msg"] = 'OK'
                    #else:
                    #res[i] = {
                    #    "ret": result.getRet(),
                    #    "msg": result.getMsg(),
                    #}
    zt_flow_value = mergeData(to_be_merged)
    res = {"bandwidth": zt_flow_value}
    return jsonify(res)