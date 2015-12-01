# -*- coding: utf-8 -*-
from __future__ import division
__author__ = 'liujiahua'
from flask import jsonify
from flask import request
import commonDomainStruct
from ztcdn.api import cdn_api
from ztcdn.util.apiUtil import getUrlHostList, verifyUrl, saveErrorTask, saveSpTask, \
    getReqStatus, getCdnClient4Task, getSpTaskId, updateTaskStatus, getUserProjByToken
import sys
import uuid
reload(sys)
sys.setdefaultencoding('utf-8')

@cdn_api.route('/purge', methods=['POST'])
def purge():
    """    从接收的 json 里生成 domain 对象
    """
    cdn_clients = []
    project_ids = []
    pid_to_save = ''
    token = request.headers.get("X-Auth-Token")
    project_id = request.json.get("project_id")
    if project_id:
        project_ids = [project_id]
        task_user = request.json.get('username')
        pid_to_save = project_id
    else:
        user = getUserProjByToken(token)
        if not user:
            return jsonify({"error": "Could not find token"}), 404
        task_user = user.username
        project_dict = user.proj_list
        for keys in project_dict:
            project_ids.append(keys)

    urls = request.json.get("urls")
    dirs = request.json.get("dirs")
    task_type = ''
    task_content = ''
    # 文件为 0 目录为 1

    if urls:
        task_type = 1
        task_content = ','.join(urls)
        host_list = getUrlHostList(urls)
        if len(host_list) != 1:
            return jsonify({"error": "A single host name can only be submitted at a time"}), 400
        verify_result = verifyUrl(host_list[0], project_ids)
        if verify_result.has_key("error"):
            return jsonify(verify_result), 403
        else:
            cdn_clients = verify_result["cdn_clients"]
            pid_to_save = verify_result["match_project"]


    if dirs:
        task_type = 0
        task_content = ','.join(dirs)
        host_list = getUrlHostList(dirs)
        if len(host_list) != 1:
            return jsonify({"error": "A single host name can only be submitted at a time"}), 400
        verify_result = verifyUrl(host_list[0], project_ids)
        if verify_result.has_key("error"):
            return jsonify(verify_result), 403
        else:
            cdn_clients = verify_result["cdn_clients"]
            pid_to_save = verify_result["match_project"]

    all_cdn_len = len(cdn_clients)
    if all_cdn_len == 0:
        return jsonify({"error": "can not found sp"}), 404
    success_cdn = 0
    res = {}
    sp_res = {}
    zt_task_id = uuid.uuid1()
    for i in cdn_clients:
        aaa = ''
        exec "import ztcdn.api." + i + ".api.domainApi as aaa"
        DomainApi = getattr(aaa, 'DomainApi')
        api = DomainApi()
        purgeBatch = commonDomainStruct.PurgeBatch(urls=urls, dirs=dirs)
        result = api.purge(purgeBatch)
        if result.getRet() == 0:
            success_cdn += 1
        else:
            error_msg = result.getMsg()
            error_code = result.getRet()
        sp_res[i] = {
                "ret": result.getRet(),
                "msg": result.getMsg(),
                "reqId": result.getXCncRequestId()
        }
    res["successRate"] = success_cdn / all_cdn_len * 100
    if success_cdn != all_cdn_len:  # 有至少一个失败了
        saveErrorTask(zt_task_id, pid_to_save, task_type, task_content, task_user)
        res["error"] = error_msg
        return jsonify(res), error_code
    else: # 都成功了， 入库
        saveSpTask(zt_task_id, pid_to_save, task_type, task_content, task_user, sp_res)
        res["reqId"] = zt_task_id
        return jsonify(res)


@cdn_api.route('/req_status/<req_id>', methods=['GET'])
def reqStatus(req_id):
    result = getReqStatus(req_id)
    if result.has_key("error"):
        return jsonify(result), 404
    else:
        return jsonify(result)


# 查询任务状态并写库的接口，不给用户的
@cdn_api.route('/purge/<purge_id>', methods=['GET'])
def purgeQueryByPurgeId(purge_id):
    """    从接收的 json 里生成 domain 对象
    """
    cdn_clients = getCdnClient4Task(purge_id)
    all_cdn_len = len(cdn_clients)
    if all_cdn_len == 0:
        return jsonify({"error": "can not found sp"}), 404
    success_cdn = 0
    res = {}
    for i in cdn_clients:
        aaa = ''
        exec "import ztcdn.api." + i + ".api.domainApi as aaa"
        DomainApi = getattr(aaa, 'DomainApi')
        api = DomainApi()
        has_success = 0
        req_result = {}
        _id = getSpTaskId(purge_id, i)
        #purge_id 就是 task_id
        result = api.purgeQueryByPurgeId(_id)
        if result.getRet() == 0:
            success_cdn += 1
            has_success = 1
            # 刷新目录和文件 itemList 只有一个元素，预缓存会有多个
            path = result.getPurgeList()[0].itemList[0].url
            status = result.getPurgeList()[0].itemList[0].status
            rate = result.getPurgeList()[0].itemList[0].rate
            req_result = {
                "reqId": _id,
                "path": path,
                "status": status,
                "rate": rate
            }
            updateTaskStatus(_id, status)
        if has_success == 1:
            res[i] = {
                    "ret": 0,
                    "msg": 'OK',
            }
        else:
            res[i] = {
                "ret": result.getRet(),
                "msg": result.getMsg(),
            }
        res[i]["result"] = req_result

    res["zt_api"] = {}
    res["zt_api"]["successRate"] = success_cdn / all_cdn_len * 100
    return jsonify(res)


@cdn_api.route('/prefetch', methods=['POST'])
def prefetch():
    """    从接收的 json 里生成 domain 对象
    """
    cdn_clients = []
    project_ids = []
    token = request.headers.get("X-Auth-Token")
    project_id = request.json.get("project_id")
    if project_id:
        project_ids = [project_id]
        task_user = request.json.get('username')
        pid_to_save = project_id
    else:
        user = getUserProjByToken(token)
        if not user:
            return jsonify({"error": "Could not find token"}), 404
        task_user = user.username
        project_dict = user.proj_list
        for keys in project_dict:
            project_ids.append(keys)

    urls = request.json.get("urls")
    task_type = '2'
    task_content = ''
    # 预缓存类型是 2

    if urls:
        task_type = '2'
        task_content = ','.join(urls)
        host_list = getUrlHostList(urls)
        if len(host_list) != 1:
            return jsonify({"error": "A single host name can only be submitted at a time"}), 400
        verify_result = verifyUrl(host_list[0], project_ids)
        if verify_result.has_key("error"):
            return jsonify(verify_result), 403
        else:
            cdn_clients = verify_result["cdn_clients"]
            pid_to_save = verify_result["match_project"]
    else:
        return jsonify({"error": "can not found key 'urls'"}), 404

    all_cdn_len = len(cdn_clients)
    if all_cdn_len == 0:
        return jsonify({"error": "can not found sp"}), 404
    success_cdn = 0
    res = {}
    sp_res = {}
    zt_task_id = uuid.uuid1()
    for i in cdn_clients:
        aaa = ''
        exec "import ztcdn.api." + i + ".api.domainApi as aaa"
        DomainApi = getattr(aaa, 'DomainApi')
        api = DomainApi()
        purgeBatch = commonDomainStruct.PurgeBatch(urls=urls)
        result = api.prefetch(purgeBatch)
        if result.getRet() == 0:
            success_cdn += 1
        else:
            error_msg = result.getMsg()
            error_code = result.getRet()
        sp_res[i] = {
                "ret": result.getRet(),
                "msg": result.getMsg(),
                "reqId": result.getXCncRequestId()
        }
    res["successRate"] = success_cdn / all_cdn_len * 100
    if success_cdn != all_cdn_len:  # 有至少一个失败了，不存副表了，只存主表
        saveErrorTask(zt_task_id, pid_to_save, task_type, task_content, task_user)
        res["error"] = error_msg.encode('utf-8')
        return jsonify(res), error_code
    else: # 都成功了， 入库
        saveSpTask(zt_task_id, pid_to_save, task_type, task_content, task_user, sp_res)
        res["reqId"] = zt_task_id
        return jsonify(res)


@cdn_api.route('/prefetch/<purge_id>', methods=['GET'])
def prefetchQueryByPurgeId(purge_id):
    cdn_clients = getCdnClient4Task(purge_id)
    all_cdn_len = len(cdn_clients)
    if all_cdn_len == 0:
        return jsonify({"error": "can not found sp"}), 404
    success_cdn = 0
    res = {}
    for i in cdn_clients:
        aaa = ''
        exec "import ztcdn.api." + i + ".api.domainApi as aaa"
        DomainApi = getattr(aaa, 'DomainApi')
        api = DomainApi()
        _id = getSpTaskId(purge_id, i)
        result = api.prefetchQueryByPurgeId(_id)
        if result.getRet() == 0:
            success_cdn += 1
            req_result = []
            status_list = []
            for j in result.getPurgeList()[0].itemList:
                return_task_item = {}
                return_task_item["path"] = j.url
                return_task_item["status"] = j.status
                return_task_item["rate"] = j.rate
                status_list.append(j.status)
                req_result.append(return_task_item)
            res[i] = {
                    "ret": 0,
                    "msg": 'OK',
                    "reqId": _id
            }
            res[i]["result"] = req_result

            # 从所有status里判断出一个status入库
            if "wait" in status_list:
                status = "wait"
            elif "run" in status_list:
                status = "run"
            elif "init" in status_list:
                status = "init"
            elif "prepare" in status_list:
                status = "prepare"
            elif "failure" in status_list:
                status = "failure"
            elif "success" in set(status_list) and len(set(status_list)) == 1:
                status = "success"
            else:
                status = 'unknow'
            updateTaskStatus(_id, status)
        else:
            res[i] = {
                "ret": result.getRet(),
                "msg": result.getMsg(),
            }
    res["zt_api"] = {}
    res["zt_api"]["successRate"] = success_cdn / all_cdn_len * 100
    return jsonify(res)