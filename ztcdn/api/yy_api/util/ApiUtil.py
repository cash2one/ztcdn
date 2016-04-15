# -*- coding: utf-8 -*-

if __name__ == '__main__':
    pass

import urlparse, httplib, time, base64, hmac, sha
from ztcdn.models import cdn_manage_sp, cdn_manage_sp_tasklist, cdn_manage_tasklist
from datetime import datetime
from ztcdn.config import logging
import urlparse

X_CNC_REQUEST_ID = 'x-cnc-request-id'
logger = logging.getLogger(__name__)

def encodePassword(pw):
    ''' 此处的 password需要 先经过base64加密 '''
    return base64.b64encode(pw)

def hashPassword(data, key):
    ''' api 中密码使用的hash算法 '''
    h = hmac.new(key, data, sha)
    return base64.encodestring(h.digest()).strip()

def httpReqeust(url, body = None, headers = None, method = "POST"):
    ''' 进行http请求 '''
    logger.debug("")
    logger.debug("url: " + str(url))
    urlList = urlparse.urlparse(url)
    logger.debug("header:" + str(headers))
    logger.debug("method: " + method)
    logger.debug("body: " + body)
    if not urlList.scheme or not urlList.netloc or not urlList.path:
        raise Exception("url 格式出错, " + url)

    if urlList.scheme == 'https':
        con = httplib.HTTPSConnection(urlList.netloc, timeout = 15)
    else:
        con = httplib.HTTPConnection(urlList.netloc, timeout = 15)
    path = urlList.path
    
    if urlList.query:
        path = path + "?" + urlList.query
    con.request(method, path, body, headers)
    res = con.getresponse()
    logger.debug("response: status:" + str(res.status) + ", reason:" + res.reason)
    return res


class BaseResult(object):
    def __init__(self, ret, msg, xCncRequestId = None):
        self.ret = ret
        self.msg= msg
        self.xCncRequestId = xCncRequestId

    def isSuccess(self):
        ''' 判断请求是否成功'''
        return self.ret == 0

    def getRet(self):
        ''' 获取返回代码'''
        return self.ret

    def getMsg(self):
        ''' 获取返回消息'''
        return self.msg

    def getXCncRequestId(self):
        ''' 返回请求的编号 '''
        return self.xCncRequestId


def getDomainNameById(domainId):
    sp_domain_obj = cdn_manage_sp.query.filter(
        cdn_manage_sp.sp_domain_id == domainId,
    ).first()
    if not sp_domain_obj:
        domain_name = ''
    else:
        domain_name = sp_domain_obj.domain_name
    return domain_name


def getDomainNameByPurgeId(purgeId):
    sp_task_obj = cdn_manage_sp_tasklist.query.filter(
        cdn_manage_sp_tasklist.sp_task_id == purgeId,
    ).first()
    task_table_id = sp_task_obj.task_table_id
    task_obj = cdn_manage_tasklist.query.filter(
        cdn_manage_tasklist.id == task_table_id
    ).first()
    task_content = task_obj.task_content
    domain_name = urlparse.urlparse(task_content.split(',')[0])[1]
    return domain_name