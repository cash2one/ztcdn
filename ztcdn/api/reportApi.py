# -*- coding: utf-8 -*-
__author__ = 'liujiahua'
from flask import jsonify
from flask import request
from ztcdn.config import logging
from ztcdn.api import cdn_api
from ztcdn.util.apiUtil import verifyUrl, mergeData, getUserProjByToken
import sys
import datetime
import json
from collections import OrderedDict

reload(sys)
sys.setdefaultencoding('utf-8')

logger = logging.getLogger(__name__)

@cdn_api.route('/flow', methods=['GET'])
def getFlow():
    if not request.json:
        return jsonify({"error": "Bad request, no json data"}), 400
    domain_names = request.json.get("domainName")
    start = request.json.get("start")
    end = request.json.get("end")
    if not domain_names or not start or not end:
        return jsonify({"error": "Bad request, please check request data"}), 400

    delta = datetime.datetime.strptime(end, '%Y-%m-%d') - datetime.datetime.strptime(start, '%Y-%m-%d')
    if delta.days > 30:
        return jsonify({"error": '查询范围请不要超过31天'.decode('utf-8')}), 400

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
    value_sum = sum([float(v['value']) for v in zt_flow_value])
    res = {"flowValue": zt_flow_value, "totalCount": value_sum}
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

    delta = datetime.datetime.strptime(end, '%Y-%m-%d') - datetime.datetime.strptime(start, '%Y-%m-%d')
    if delta.days > 30:
        return jsonify({"error": '查询范围请不要超过31天'.decode('utf-8')}), 400

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


@cdn_api.route('/get_price/<month>', methods=['GET'])
def get_price(month):
    if not month:
        return jsonify({"error": "can not found month"}), 400

    try:
        import os
        a = os.popen('/root/shiwenjun/sum_game.sh %s' % month)
        detail = []
        for i in a.readlines():
            j = i.split()
            detail.append(
                {
                    "domain": j[0],
                    "project_name": j[1],
                    "month": j[2],
                    "type": j[3],
                    "price": j[4]
                }
            )
        return jsonify({'code': 200, 'msg': '',
                        'detail': json.loads(json.dumps(detail, ensure_ascii=False), 'gbk')})
    except:
        logger.exception('Error with get price')
        return jsonify({'code': 404, 'msg': 'can not found bill'}), 404