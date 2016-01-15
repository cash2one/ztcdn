# -*- coding: utf-8 -*-
from __future__ import division

__author__ = 'liujiahua'
from ztcdn.api.commonDomainStruct import Domain, CacheBehavior, OriginConfig, User
from flask import jsonify
from ztcdn.models import cdn_manage_domain, cdn_manage_sp, cdn_manage_sp_choose, cdn_manage_cacherules, \
    cdn_manage_tasklist, cdn_manage_sp_tasklist, cdn_manage_log
from ztcdn import db
import copy
import uuid
import datetime
import json
import httplib
import urlparse
import sys, traceback
from ztcdn.config import AUTH_PUBLIC_URI, ADMIN_TOKEN, ADMIN_PROJ
from collections import OrderedDict
from cname import CName


def getUserProjByToken(token):
    headers = {"X-Auth-Token": "%s" % ADMIN_TOKEN}
    KEYSTONE = AUTH_PUBLIC_URI
    if token == ADMIN_TOKEN:
        user = User(token, 'admin', {ADMIN_PROJ: 'admin'})
        return user
    try:
        conn = httplib.HTTPConnection(KEYSTONE)
    except:
        return 'ConnError'
    try:
        conn.request("GET", "/v2.0/tokens/%s" % token, '', headers)
    except:
        return 'ConnError'
    response = conn.getresponse()
    data = response.read()
    dd = json.loads(data)
    try:
        apitoken = dd['access']['token']['id']
        user_id = dd['access']['user']['id']
        username = dd['access']['user']['username']
    except Exception, e:
        traceback.print_exc(file=sys.stdout)
        return None
    rq_headers = {"X-Auth-Token": "%s" % apitoken}
    conn.request('GET', '/v3/users/%s/projects' % user_id, '', rq_headers)
    resp = conn.getresponse().read()
    result = json.loads(resp)
    project_dict = {}
    for p in result["projects"]:
        project_dict[p["id"]] = p["name"]
    conn.close()
    user = User(apitoken, username, project_dict)
    return user


def getTokenFromKS(username, password):
    headers = {"Content-type": "application/json"}
    KEYSTONE = AUTH_PUBLIC_URI
    try:
        conn = httplib.HTTPConnection(KEYSTONE)
    except:
        return 'ConnError'
    params = '{"auth": {"passwordCredentials": {"username": "%s", "password": "%s"}}}' % (username, password)
    try:
        conn.request("POST", "/v2.0/tokens", params, headers)
    except:
        return 'ConnError'
    response = conn.getresponse()
    data = response.read()
    dd = json.loads(data)
    return dd


def jsonToDomain(domainNode):
    domainName = domainNode.get("domainName")
    serviceType = domainNode.get("serviceType", "web")
    etag = domainNode.get("etag")
    testUrl = domainNode.get("testUrl")
    domainId = domainNode.get("domainId")
    comment = domainNode.get("comment", "create")
    status = domainNode.get("status")
    enabled = domainNode.get("enabled", "True")
    cname = domainNode.get("cname")
    cacheBehaviors = domainNode.get("cacheBehaviors")
    originIps = domainNode.get("originIps")
    originConfig = OriginConfig(originIps=originIps)

    domain = Domain(
        domainName=domainName,
        serviceType=serviceType,
        domainId=domainId,
        etag=etag,
        testUrl=testUrl,
        comment=comment,
        status=status,
        enabled=enabled,
        cname=cname,
        originConfig=originConfig
    )

    if cacheBehaviors:
        cacheBehaviorsList = []
        for i in cacheBehaviors:
            pathPattern = i.get("pathPattern")
            ignoreCacheControl = i.get("ignoreCacheControl")
            cacheTtl = i.get("cacheTtl")
            cacheBehavior = CacheBehavior(pathPattern=pathPattern, ignoreCacheControl=ignoreCacheControl,
                                          cacheTtl=cacheTtl)
            cacheBehaviorsList.append(cacheBehavior)
        domain.cacheBehaviors = cacheBehaviorsList
    return domain


def getCdnClients(domain=None, domain_id=None):
    cdn_clients = ''
    if domain:
        service_type = domain.serviceType
        query_obj = db.session.query(cdn_manage_sp_choose).filter(
            cdn_manage_sp_choose.service_type == service_type
        ).first()
        cdn_clients = query_obj.used_sp_list.split(',')
    if domain_id:
        query_obj = db.session.query(cdn_manage_domain).filter(
            cdn_manage_domain.domain_id == domain_id
        ).first()
        service_type = query_obj.domain_type
        query_obj = db.session.query(cdn_manage_sp_choose).filter(
            cdn_manage_sp_choose.service_type == service_type
        ).first()
        cdn_clients = query_obj.used_sp_list.split(',')
    return cdn_clients


def getCdnClientsFromDB(domain=None, domain_id=None):
    if domain:
        zt_domain_id = domain.domainId
    else:
        zt_domain_id = domain_id

    this_domain_obj = cdn_manage_domain.query.filter_by(domain_id=zt_domain_id)
    if not this_domain_obj:
        cdn_clients = ''
    else:
        domain_table_id = this_domain_obj.first().id
        # 拿着这个主表的table id 去副表查有哪些厂商
        query_obj = cdn_manage_sp.query.filter(
            cdn_manage_sp.domain_table_id == domain_table_id,
            cdn_manage_sp.sp_domain_status != 'Delete',
        )
        # 假如不存在，则返回 false
        if not query_obj:
            cdn_clients = ''
        else:
            all_sp = query_obj.all()
            cdn_clients = [i.sp_domain_type for i in all_sp]

    return cdn_clients


def getSpDomainId(domain_id, sp_domain_type):
    domain_obj = cdn_manage_domain.query.filter_by(domain_id=domain_id).first()
    domain_name = domain_obj.domain_name
    sp_domain_obj = cdn_manage_sp.query.filter_by(domain_name=domain_name, sp_domain_type=sp_domain_type).first()
    _id = sp_domain_obj.sp_domain_id
    return _id


def getSpTaskId(zt_task_id, sp_domain_type):
    zt_task_obj = cdn_manage_tasklist.query.filter_by(task_id=zt_task_id)
    if not zt_task_obj:
        _id = ''
    else:
        task_table_id = zt_task_obj.first().id
        sp_task_obj = cdn_manage_sp_tasklist.query.filter_by(task_table_id=task_table_id,
                                                             sp_domain_type=sp_domain_type)
        if not sp_task_obj:
            _id = ''
        else:
            _id = sp_task_obj.first().sp_task_id
    return _id


def addResult(domain, project_id, username):
    cdn_clients = getCdnClients(domain=domain)
    all_cdn_len = len(cdn_clients)
    success_cdn = 0
    res = {}
    zt_domain_id = uuid.uuid1()
    for i in cdn_clients:
        aaa = ''
        exec "import ztcdn.api." + i + ".api.domainApi as aaa"
        DomainApi = getattr(aaa, 'DomainApi')
        api = DomainApi()
        result = ''
        has_success = 0
        result = api.add(domain)
        if result.getRet() == 0:
            success_cdn += 1
            saveAddDomainToDB(result.domain, i, zt_domain_id, project_id, username)
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
        if result.domain:
            res[i]["domain"] = {
                "domain_name": result.domain.domainName,
                "domain_status": result.domain.status,
                "domain_cname": result.domain.cname,
                "domain_id": result.domain.domainId,
                "enabled": result.domain.enabled,
            }
            if hasattr(result.domain, 'testUrl'):
                res[i]["domain"]["testUrl"] = result.domain.testUrl
            if hasattr(result.domain, 'serviceType'):
                res[i]["domain"]["serviceType"] = result.domain.serviceType
            if hasattr(result.domain, 'comment'):
                res[i]["domain"]["comment"] = result.domain.comment
            if result.domain.originConfig != None:
                res[i]["domain"]["originIps"] = result.domain.originConfig.originIps
            if result.domain.etag != None:
                res[i]["domain"]["etag"] = result.domain.etag
            if result.domain.cacheBehaviors:
                cacheBehaviors = []
                for c in result.domain.cacheBehaviors:
                    cacheBehavior = {}
                    cacheBehavior["pathPattern"] = c.pathPattern
                    cacheBehavior["ignoreCacheControl"] = c.ignoreCacheControl
                    cacheBehavior["cacheTtl"] = c.cacheTtl
                    cacheBehaviors.append(cacheBehavior)
                res[i]["domain"]["cacheBehaviors"] = cacheBehaviors
    res["domain"] = {
        "domain_id": zt_domain_id,
    }
    res["successRate"] = success_cdn / all_cdn_len * 100
    if success_cdn == 0:
        res_error = {"error": result.getMsg()}
        return jsonify(res_error), result.getRet()
    else:
        # 插入 cname
        cname = CName()
        cname.insert_cname(zt_domain_id)
        return jsonify(res), 201


def commonResult(cdnAct, domain=None, domain_id=None):
    # domain 和 domain_id 肯定会有一个传进来，根据这个去 DB 获取 cdn_clients
    cdn_clients = ''
    if domain:
        cdn_clients = getCdnClientsFromDB(domain=domain)
    if domain_id:
        cdn_clients = getCdnClientsFromDB(domain_id=domain_id)
    if not cdn_clients:
        return jsonify({"error": "sp can not found"}), 404
    all_cdn_len = len(cdn_clients)
    success_cdn = 0
    res = {}
    for i in cdn_clients:
        aaa = ''
        exec "import ztcdn.api." + i + ".api.domainApi as aaa"
        DomainApi = getattr(aaa, 'DomainApi')
        api = DomainApi()
        result = ''
        has_success = 0
        if cdnAct == "find":
            # 传入了 domain_id, 这个 id 是 zt_domain_id
            _id = getSpDomainId(domain_id, i)
            result = api.find(_id)
            if result.getRet() == 0:
                success_cdn += 1
                has_success = 1
                saveFindDomainToDB(result.domain, i, domain_id)

        if cdnAct == "modify":
            # 传入了 domain 对象
            domain_id = domain.domainId
            _id = getSpDomainId(domain_id, i)
            c = copy.deepcopy(domain)
            c.domainId = _id
            result = api.modify(c)
            if result.getRet() == 0:
                success_cdn += 1
                # 来一遍 find 以更新库
                find_result = api.find(_id)
                if find_result.getRet() == 0:
                    saveFindDomainToDB(find_result.domain, i, domain_id, is_updated=True)

        if cdnAct == "delete":
            _id = getSpDomainId(domain_id, i)
            result = api.delete(_id)
            if result.getRet() == 0:
                success_cdn += 1
                saveDeleteSpDomainToDB(_id)

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
        if result.domain:
            res[i]["domain"] = {
                "domain_name": result.domain.domainName,
                "domain_status": result.domain.status,
                "domain_cname": result.domain.cname,
                "domain_id": result.domain.domainId,
                "enabled": result.domain.enabled,
            }
            if hasattr(result.domain, 'testUrl'):
                res[i]["domain"]["testUrl"] = result.domain.testUrl
            if hasattr(result.domain, 'serviceType'):
                res[i]["domain"]["serviceType"] = result.domain.serviceType
            if hasattr(result.domain, 'comment'):
                res[i]["domain"]["comment"] = result.domain.comment
            if result.domain.originConfig != None:
                res[i]["domain"]["originIps"] = result.domain.originConfig.originIps
            if result.domain.etag != None:
                res[i]["domain"]["etag"] = result.domain.etag
            if result.domain.cacheBehaviors:
                cacheBehaviors = []
                for c in result.domain.cacheBehaviors:
                    cacheBehavior = {}
                    cacheBehavior["pathPattern"] = c.pathPattern
                    cacheBehavior["ignoreCacheControl"] = c.ignoreCacheControl
                    cacheBehavior["cacheTtl"] = c.cacheTtl
                    cacheBehaviors.append(cacheBehavior)
                res[i]["domain"]["cacheBehaviors"] = cacheBehaviors
    res["domain"] = {
        "domain_id": domain_id,
    }
    res["successRate"] = success_cdn / all_cdn_len * 100
    if cdnAct == "delete" and success_cdn == all_cdn_len:
        # 各厂商CDN都删除成功，设置主表状态为Delete
        # 并且删除 CName
        cname = CName()
        cname.del_cname(domain_id)
        saveDeleteDomainToDB(domain_id)
    if success_cdn != all_cdn_len:
        res_error = {"error": result.getMsg()}
        return jsonify(res_error), result.getRet()
    else:
        return jsonify(res)


def saveAddDomainToDB(domain, sp_type, zt_domain_id, project_id, username):
    domain_name = domain.domainName
    domain_type = domain.serviceType
    domain_status = domain.status

    # sp 部分
    domain_cname = domain.cname
    sp_type = sp_type
    sp_domain_id = domain.domainId
    etag = domain.etag

    domain_id = zt_domain_id
    ip_list = ','.join(domain.originConfig.originIps)

    new_domain_exist = db.session.query(cdn_manage_domain).filter(
        cdn_manage_domain.domain_id == domain_id
    ).first()

    if not new_domain_exist:
        new_domain = cdn_manage_domain(domain_name=domain_name, domain_type=domain_type,
                                       domain_status=domain_status, domain_id=domain_id,
                                       ip_list=ip_list, project_id=project_id, user_name=username,
                                       create_time=datetime.datetime.now())
        db.session.add(new_domain)
        db.session.commit()
        domain_table_id = new_domain.id
    else:
        domain_table_id = db.session.query(cdn_manage_domain).filter(
            cdn_manage_domain.domain_id == domain_id
        ).first().id

    new_sp_domain = cdn_manage_sp(domain_name=domain_name, domain_cname=domain_cname,
                                  sp_domain_type=sp_type, sp_domain_status=domain_status,
                                  sp_domain_id=sp_domain_id, sp_etag=etag, domain_table_id=domain_table_id)
    db.session.add(new_sp_domain)
    db.session.commit()

    if hasattr(domain, 'testUrl'):
        testUrl = domain.testUrl
        db.session.query(cdn_manage_domain).filter(cdn_manage_domain.id == domain_table_id).update({
            cdn_manage_domain.test_url: testUrl
        })
        db.session.commit()

    # 缓存策略无论有几家厂商只存一次，由主表域名判定是否存过
    if domain.cacheBehaviors and not new_domain_exist:
        for c in domain.cacheBehaviors:
            pathPattern = c.pathPattern
            pathPattern = pathPattern.replace('/.', '.')
            if c.ignoreCacheControl == "True":
                ignoreCacheControl = "True"
            else:
                ignoreCacheControl = "False"
            cacheTtl = c.cacheTtl
            new_cache_rules = cdn_manage_cacherules(cache_path=pathPattern,
                                                    ignore_param_req=ignoreCacheControl,
                                                    cache_time=cacheTtl,
                                                    domain_table_id=domain_table_id)
            db.session.add(new_cache_rules)
        db.session.commit()


def saveFindDomainToDB(domain, sp_type, zt_domain_id, is_updated=False):
    domain_status = domain.status

    # sp 部分
    domain_cname = domain.cname
    sp_type = sp_type
    sp_domain_id = domain.domainId
    etag = domain.etag
    update_time = datetime.datetime.now()
    domain_id = zt_domain_id
    ip_list = ','.join(domain.originConfig.originIps)

    modify_domain = db.session.query(cdn_manage_domain).filter(
        cdn_manage_domain.domain_id == domain_id
    ).first()
    domain_table_id = modify_domain.id

    # 更新域名主表
    if is_updated:
        modify_domain.domain_status = 'InProgress'
    if modify_domain.ip_list != ip_list:
        modify_domain.ip_list = ip_list
    modify_domain.update_time = update_time

    if hasattr(domain, 'testUrl'):
        testUrl = domain.testUrl
        modify_domain.test_url = testUrl
    db.session.commit()

    # 更新厂商表
    modify_sp_domain = db.session.query(cdn_manage_sp).filter(
        cdn_manage_sp.domain_table_id == domain_table_id,
        cdn_manage_sp.sp_domain_type == sp_type,
    ).first()
    if modify_sp_domain.domain_cname != domain_cname:
        modify_sp_domain.domain_cname = domain_cname
    if modify_sp_domain.sp_domain_status != domain_status:
        modify_sp_domain.sp_domain_status = domain_status
    if modify_sp_domain.sp_etag != etag:
        modify_sp_domain.sp_etag = etag
    if modify_sp_domain.sp_domain_id != sp_domain_id:
        modify_sp_domain.sp_domain_id = sp_domain_id
    db.session.commit()

    # 判断缓存是否有更新
    if not domain.cacheBehaviors:
        old_cache_obj = cdn_manage_cacherules.query.filter_by(domain_table_id=domain_table_id).all()
        if len(old_cache_obj) > 0:
            for c in old_cache_obj:
                db.session.delete(c)
        db.session.commit()

    if domain.cacheBehaviors:
        db_cache_obj = cdn_manage_cacherules.query.filter_by(domain_table_id=domain_table_id).all()
        db_cache_list = []
        db_cache_dict = {}
        for d in db_cache_obj:
            db_cache_dict["cache_path"] = d.cache_path
            db_cache_dict["ignore_param_req"] = d.ignore_param_req
            db_cache_dict["cache_time"] = d.cache_time
        db_cache_list.append(db_cache_dict)

        return_cache_list = []
        return_cache_dict = {}
        for r in domain.cacheBehaviors:
            return_cache_dict["cache_path"] = r.pathPattern
            if r.ignoreCacheControl == "True":
                ignoreCacheControl = "True"
            else:
                ignoreCacheControl = "False"
            return_cache_dict["ignore_param_req"] = ignoreCacheControl
            return_cache_dict["cache_time"] = r.cacheTtl
        return_cache_list.append(return_cache_dict)

        if db_cache_list != return_cache_list:
            # 更新缓存，先删除这个域名的所有缓存再重新存入
            old_cache_obj = cdn_manage_cacherules.query.filter_by(domain_table_id=domain_table_id).all()
            if len(old_cache_obj) > 0:
                for c in old_cache_obj:
                    db.session.delete(c)
                db.session.commit()

            current_cache_obj = cdn_manage_cacherules.query.filter_by(domain_table_id=domain_table_id).first()
            if domain.cacheBehaviors and not current_cache_obj:
                for c in domain.cacheBehaviors:
                    pathPattern = c.pathPattern
                    if c.ignoreCacheControl == "True":
                        ignoreCacheControl = "True"
                    else:
                        ignoreCacheControl = "False"
                    cacheTtl = c.cacheTtl
                    new_cache_rules = cdn_manage_cacherules(cache_path=pathPattern,
                                                            ignore_param_req=ignoreCacheControl,
                                                            cache_time=cacheTtl,
                                                            domain_table_id=domain_table_id)
                    db.session.add(new_cache_rules)
                db.session.commit()


def saveDeleteSpDomainToDB(sp_domain_id):
    db.session.query(cdn_manage_sp).filter(cdn_manage_sp.sp_domain_id == sp_domain_id).update({
        cdn_manage_sp.sp_domain_status: "Delete"
    })
    db.session.commit()


def saveDeleteDomainToDB(zt_domain_id):
    db.session.query(cdn_manage_domain).filter(cdn_manage_domain.domain_id == zt_domain_id).update({
        cdn_manage_domain.domain_status: "Delete"
    })
    db.session.commit()


# 获取刷新缓存或者预缓存的域名列表
def getUrlHostList(url_list):
    host_list = []
    for u in url_list:
        host = urlparse.urlsplit(u)[1].split(':')[0]
        host_list.append(host)
    host_list_set = [i for i in set(host_list)]
    return host_list_set


# 判断用户刷新的url是不是他自己建立的, 如果是，返回可以刷新的厂商
def verifyUrl(host, project_ids):
    is_yours = 0
    cdn_clients = []
    # 找到与域名匹配的 project_id
    match_project = ''
    for pid in project_ids:
        if pid == '1234567890':
            db_query = cdn_manage_domain.query.filter(
                cdn_manage_domain.domain_name == host,
                cdn_manage_domain.domain_status == 'Deployed'
            ).all()
        else:
            db_query = cdn_manage_domain.query.filter(
                cdn_manage_domain.domain_name == host,
                cdn_manage_domain.project_id == pid,
                cdn_manage_domain.domain_status == 'Deployed'
            ).all()
        if len(db_query) > 0:
            is_yours += 1
            match_project = pid
            _id = db_query[0].id
            sp_domain = cdn_manage_sp.query.filter(
                cdn_manage_sp.domain_table_id == _id,
                cdn_manage_sp.sp_domain_status == 'Deployed'
            ).all()
            for s in sp_domain:
                cdn_clients.append(s.sp_domain_type)

    if is_yours == 1:
        return {"cdn_clients": cdn_clients, "match_project": match_project}
    else:
        return {"error": host + " is not yours or not ready"}


# 刷新缓存，有失败的，则不保存到副表，直接存入主表 error
def saveErrorTask(zt_task_id, project_id, task_type, task_content, task_user):
    new_task = cdn_manage_tasklist(
        task_id=zt_task_id,
        project_id=project_id,
        task_type=task_type,
        task_status='error',
        task_content=task_content,
        task_user=task_user,
        task_create_at=datetime.datetime.now(),
    )
    db.session.add(new_task)
    db.session.commit()


# 刷新缓存(几个厂商都刷新成功了)，存入request id 到 2 个 db
def saveSpTask(zt_task_id, project_id, task_type, task_content, task_user, res):
    new_task = cdn_manage_tasklist(
        task_id=zt_task_id,
        project_id=project_id,
        task_type=task_type,
        task_status='run',
        task_content=task_content,
        task_user=task_user,
        task_create_at=datetime.datetime.now(),
    )
    db.session.add(new_task)
    db.session.commit()

    task_table_id = cdn_manage_tasklist.query.filter_by(task_id=zt_task_id).first().id
    for key in res:
        if key == "zt_api":
            continue
        new_sp_task = cdn_manage_sp_tasklist(
            task_table_id=task_table_id,
            sp_task_id=res[key]["reqId"],
            sp_domain_type=key,
            sp_task_type=task_type,
            sp_task_status="run",
        )
        db.session.add(new_sp_task)
        db.session.commit()


# 根据请求Id去拿任务状态，包括刷新缓存，刷新目录，预缓存, 给用户用的
def getReqStatus(req_id):
    result = {}
    task_obj = cdn_manage_tasklist.query.filter_by(task_id=req_id).first()
    if not task_obj:
        result = {"error": "task id can not found"}
    else:
        result = {"task": {
            "taskId": task_obj.task_id,
            "projectId": task_obj.project_id,
            "taskType": task_obj.task_type,
            "taskContent": task_obj.task_content,
            "taskStatus": task_obj.task_status,
            "taskUser": task_obj.task_user,
            "taskCreateAt": task_obj.task_create_at,
            "taskDoneAt": task_obj.task_done_at
        }
        }

    return result


# 根据任务ID查询有哪些厂商
def getCdnClient4Task(zt_task_id):
    cdn_clients = ''
    zt_task_obj = cdn_manage_tasklist.query.filter_by(task_id=zt_task_id).first()
    if not zt_task_obj:
        task_table_id = ''
    else:
        task_table_id = zt_task_obj.id

    sp_task_objs = cdn_manage_sp_tasklist.query.filter_by(task_table_id=task_table_id).all()
    if not sp_task_objs:
        cdn_clients = ''
    else:
        all_sp_tasks = sp_task_objs
        cdn_clients = [i.sp_domain_type for i in all_sp_tasks]

    return cdn_clients


# 由 zt_task_id 更新每个厂商任务状态
def updateTaskStatus(sp_task_id, task_status):
    sp_task_obj = db.session.query(cdn_manage_sp_tasklist).filter_by(
        sp_task_id=sp_task_id
    ).first()

    if sp_task_obj.sp_task_status != task_status:
        sp_task_obj.sp_task_status = task_status
        if task_status == "success" or task_status == "failure" or task_status == "delete":
            now = datetime.datetime.now()
            sp_task_obj.task_done_at = now
        db.session.commit()


# ################ 以下为流量所用 ##############

# 根据域名查询有哪些厂商
def getCdnClientByName(domainName):
    cdn_clients = ''
    zt_domain_obj = cdn_manage_domain.query.filter(
        cdn_manage_domain.domain_name == domainName,
        cdn_manage_domain.domain_status != 'Delete'
    ).first()
    if not zt_domain_obj:
        domain_table_id = ''
    else:
        domain_table_id = zt_domain_obj.id

    sp_domain_objs = cdn_manage_sp.query.filter_by(domain_table_id=domain_table_id).all()
    if not sp_domain_objs:
        cdn_clients = ''
    else:
        all_sp_domains = sp_domain_objs
        cdn_clients = [i.sp_domain_type for i in all_sp_domains]

    return cdn_clients


# 合并流量、带宽数据
def mergeData(dataList):
    # 找到最长的元素
    longest_dict = OrderedDict()
    for d in dataList:
        if len(d) > len(longest_dict):
            longest_dict = d

    merged_data = []
    for key in longest_dict:
        item = {}
        sum = 0
        for j in dataList:
            value = float(j.get(key, 0))
            sum += value
        item["time"] = key
        item["value"] = str(sum)
        merged_data.append(item)
    return merged_data


# 日志分析，从 DB 获取 url 的访问次数和流量，以及 top 10
def get_cdn_log(domain_name, start, end):
    log_obj = cdn_manage_log.query.filter(
        cdn_manage_log.domain_name == domain_name,
        cdn_manage_log.date >= start,
        cdn_manage_log.date <= end
    ).all()

    if log_obj:
        all_dict = {}
        for i in log_obj:
            if all_dict.has_key(i.url):
                all_dict[i.url] = [all_dict[i.url][0] + i.flow, all_dict[i.url][1] + i.count]
            else:
                all_dict[i.url] = [i.flow, i.count]
        # 字典转为列表并排序
        list_to_sorted = []
        for _key in all_dict:
            list_to_sorted.append((_key, round(all_dict[_key][0], 2), all_dict[_key][1]))
        list_sorted = sorted(list_to_sorted, key=lambda item: item[2])
        list_sorted.reverse()
        top_10 = list_sorted[:10]
        if len(top_10) != 10:
            while len(top_10) == 10:
                top_10.append('null')

        result = {"top_10": top_10,
                  "url_list": list_sorted}
        return result
    else:
        return {"top_10": '', "url_list": ''}
