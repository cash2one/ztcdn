# -*- coding: utf-8 -*-
'''
Created on 2013-10-14

@author: zzh
@version: 1.0
'''

import sys, logging, ztcdn.api.dl_api.util.ApiUtil as util, xml.dom as dom, xml.dom.minidom as minidom
import traceback, base64
from ztcdn.api.dl_api.util.ApiUtil import BaseResult
import httplib
import hashlib

REQ_DICT = {
    "prefetch_progress":{
        "rq_url":"/DnionCloud/cdnPrefetch/progress?RequestId=%s", #RequestId
        "type":"POST",
        "postfile":"n",
    },
    "prefetch":{
        "rq_url":"/DnionCloud/cdnPrefetch/cdnBodyPrefetch",
        "type":"POST",
        "postfile":"n",
    },
    "progress":{
         "rq_url":"/DnionCloud/cdnPush/progress?RequestId=%s", #RequestId
         "type":"POST",
         "postfile":"n",
    },
    "push":{
        "rq_url":"/DnionCloud/cdnPush/cdnUrlPush?type=%s&url=%s&decode=y", #tftype & url
        "type":"POST",
        "postfile":"n",
    }
}

logging.basicConfig(level = logging.ERROR)
logger = logging.getLogger('ws.report')

X_CNC_REQUEST_ID = 'X-Dnion-Request-Id'

X_CNC_DATE = 'Date'

X_CNC_LOCATION = 'location'



class Purge(object):
    ''' purge记录条目，用于查询 purge请求执行结果 '''
    def __init__(self, purgeId = None, requestDate = None, itemList = None):
        '''初始化
        @param purgeId: 缓存刷新的id
        @param requestDate: 缓存刷新请求的时间
        @type itemList: list of PurgeItem
        @param itemList: 该purge记录条目的 详细记录条目 的列表,即PurgeItem对象实例列表
        '''
        self.purgeId = purgeId
        self.requestDate = requestDate
        self.itemList = itemList

class PurgeItem(object):
    '''purge记录条目 中 的详细记录条目'''
    def __init__(self, url = None, status = None, rate = None, isdir = None):
        '''初始化
        @param url: 获取文件或者目录的url
        @param status: 获取当前执行状态
        @param rate: 获取执行结果，如成功率为99%时，返回99.0
        @param isdir: Y or N , indicating whether the entity is directory
        '''
        self.url = url
        self.status = status
        self.rate = rate
        self.isdir = isdir

class PurgeBatch(object):
    '''批量清楚cache缓存文件，支持对文件或者目录的purge请求'''
    def __init__(self, urls = None, dirs = None):
        '''初始化
        @type urls: list of str
        @param urls: 设置需要purge的文件url
        @type dirs: list of str
        @param dirs: 设置需要purge的目录url
        '''
        self.urls = urls
        self.dirs = dirs

class PurgeApi(object):
    '''缓存操作API'''
    
    def __init__(self, domain_name=None, domain_ip=None, test_url=None):
        self.domain_name = domain_name
        self.domain_ip = domain_ip
        self.test_url = test_url
        self.key = '1234567890abcdef'
        self.credential = 'accesskeyidexample6/20150714233600/xnop015/dnioncloud'

    def hex_digest(self, algrithom, data_list):
        try:
            hash_obj = hashlib.new(algrithom)
            for item in data_list:
                    hash_obj.update(item)
            digest = hash_obj.hexdigest()
        except Exception, e:
            return None
        return digest

    def calcSignature(self, algorithm, method, url, body=''):
        body_digest = self.hex_digest(algorithm, body)
        data_list = []
        data_list.append(method + '\n')
        data_list.append(self.key + '\n')
        data_list.append(url + '\n')
        data_list.append(body_digest + '\n')
        data_list.append(self.credential)
        signature = self.hex_digest(algorithm, data_list)
        return signature

    def req(self, type, rq_url, rq_body='', ETag=None):
        signature = self.calcSignature('md5', type, rq_url, rq_body)
        authorization = 'Algorithm=md5,Credential=' + self.credential  \
                        + ',Signature='+ signature
        rq_headers = {"Content-type": "application/xml", "Accept": "text/plain" ,"If-Match":ETag }
        rq_headers['Authorization'] = authorization
        try:
            httpClient = httplib.HTTPConnection('dcloud.dnion.com')
            httpClient.request(type , rq_url, rq_body, rq_headers)
            res = httpClient.getresponse()
            return res
        except Exception,e:
            logger.error('can not connect to dilian %s' % e)


    def purge(self, purgeBatch, domainId = None):
        '''  批量清除缓存
        @param domainId: 如果指定了domainId，http body中的file-path和dir-path仅需要提供文件或者目录的uri，
         不能包括域名名称，路径均需以/开始，如/test/a.html 如果未指定domainId, 均需要提供包括域名在内的完整url地址，
         如http://www.baidu.com/test/a.html
        @type purgeBatch: PurgeBatch
        @param purgeBatch 为 PurgeBatch对象 包含files 和 dirs属性
        @rtype: PurgeResult
        @return: 返回PurgeResult结果, 可以通过PurgeResult.getLocation 获得该次缓存
        帝联：0 是目录， 1 是文件
        '''
        url_type = 2
        url_list = []
        if purgeBatch.urls is not None:
            url_type = 1
            url_list = purgeBatch.urls
        if purgeBatch.dirs is not None:
            url_type = 0
            url_list = purgeBatch.dirs
        url_str = ','.join(url_list)
        type = REQ_DICT['push']['type']
        rq_url = REQ_DICT['push']['rq_url'] % (url_type, url_str)
        rq_body = ''
        try:
            ret = self.req(type, rq_url, rq_body)
            if ret.status == 200:
                return purgeXmlToSuccess(ret)
            else:
                return purgeXmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file = sys.stdout)
            return PurgeResult(-1, str(e))

    def pushProgress(self, req_id):

        response, resp = self.req(type, rq_url, rq_body)
        status = response.status
        reason = response.reason
        logger.info("UrlProgerss Request Url: %s" % rq_url)
        logger.info("UrlProgress status:%s, req_id: %s, reason:%s, resp:%s" % (status, req_id, reason, resp))
        return (status, reason, resp)

    def purgeQueryByPurgeId(self, purgeId):
        ''' 根据purgeId 查询 缓存记录
        @param purgeId: 缓存id
        @rtype: PurgeQueryResult 
        @return: 返回PurgeQueryResult结果,可以 通过PurgeQueryResult.getPurgeList()获取purge记录条目的列表
        '''
        try:
            type = REQ_DICT['progress']['type']
            rq_url = REQ_DICT['progress']['rq_url'] % purgeId
            rq_body = ''
            ret = self.req(type, rq_url, rq_body)
            if ret.status == 200:
                return purgeQueryByPurgeIdXmlToPurgeList(ret, purgeId)
            else:
                return purgeQueryByPurgeIdXmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return PurgeQueryResult(-1, str(e))
    
    def purgeQuery(self, dateFrom, dateTo, queryUrl = None):
        '''  查询缓存记录
        @param queryUrl 查询的url 可为空,若为空,返回该用户所有url的缓存记录
        @param dateFrom 查询时间起始  eg:'2013-10-01 01:00:00'
        @param dateTo    查询时间起始 eg:'2013-10-07 01:00:00'
        @rtype: PurgeQueryResult
        @return: 返回PurgeQueryResult结果,可以 通过PurgeQueryResult.getPurgeList()获取purge记录条目的列表
        '''
        url = self.HOST + "/api/purge"
        try:
            url = appendParams(url, queryUrl, dateFrom, dateTo)
            ret = util.httpReqeust(url, "", self.makeHeaders(), "GET")
            if ret.status == 200:
                return purgeQueryXmlToPurgeList(ret)
            else:
                return purgeQueryXmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return PurgeQueryResult(-1, str(e))
    
    def makeHeaders(self):  
        ''' 组装头部 '''  
        global X_CNC_DATE
        headers = self.headers.copy()
        headers[X_CNC_DATE] = util.getRFCTime()
        key = util.hashPassword(headers[X_CNC_DATE], self.apiKey)
        headers['Authorization'] = "Basic " + base64.standard_b64encode(self.user + ':' + key)
        return headers

def appendParams(url, queryUrl, dateFrom, dateTo):
    url = url + "?datefrom=" + util.getRFC3339Time(dateFrom).replace('+', "%2B") + "&dateto=" + util.getRFC3339Time(dateTo).replace('+', "%2B")
    if queryUrl is not None:
        queryUrl = queryUrl.replace(':', '%3A').replace('/', '%2F')
        url = url + "&url=" + queryUrl
    return url

def purgeQueryXmlToFailure(ret):
    ''' 返回xml 解析 带错误信息的 缓存查询返回xml'''
    msg = util.getReturnXmlMsg(ret)
    return PurgeQueryResult(ret.status, ret.reason + ":" + msg)

def purgeQueryByPurgeIdXmlToFailure(ret):
    ''' 返回xml 解析 带错误信息的 根据purgeId缓存查询返回xml'''
    msg = util.getReturnXmlMsg(ret)
    return PurgeQueryResult(ret.status, ret.reason + ":" + msg)

def purgeXmlToSuccess(ret):
    ''' 返回xml 转换成 成功返回的PurgeResult对象'''
    global X_CNC_REQUEST_ID, X_CNC_LOCATION
    requestId = ret.getheader(X_CNC_REQUEST_ID)
    location = ret.getheader(X_CNC_LOCATION)
    msg = util.getPurgeReturnXmlMsg(ret)
    return PurgeResult(ret.status, msg, xCncRequestId = requestId, location = location)

def purgeXmlToFailure(ret):
    ''' 返回xml 转换成带错误信息的PurgeResult对象'''
    msg = util.getReturnXmlMsg(ret)
    return PurgeResult(ret.status, ret.reason + ":" + msg)

class PurgeQueryResult(BaseResult):
    ''' 缓存查询返回结果
    '''
    def __init__(self, ret, msg, xCncRequestId = None, purgeList = None):
        '''初始化
        @type purgeList: list of Purge
        @param purgeList: 缓存查询返回的purge记录条目的列表.如果是根据purgeId查询缓存记录,则purgeList 中只有一个purge记录
        '''
        super(PurgeQueryResult, self).__init__(ret, msg, xCncRequestId)
        self.purgeList = purgeList
    def getPurgeList(self):
        '''通过getPurgeList方法获得返回结果中的purge记录条目列表'''
        return self.purgeList  
    
class PurgeResult(BaseResult):
    ''' 清除缓存返回结果
    '''
    def __init__(self, ret, msg, xCncRequestId = None, location = None):
        '''初始化
        @type location: str
        @param location: 响应头中有Location信息，使用该URL可以查询本次purge请求的执行结果，purge-id为UUID类型；
        ''' 
        super(PurgeResult, self).__init__(ret, msg, xCncRequestId)
        self.location = location
    def getLocation(self):
        '''通过getLocation()获得Location信息'''
        return self.location  

def purgeQueryXmlToPurgeList(ret):
    ''' 缓存查询 xml结果解析成 Purge对象的列表'''
    
    global X_CNC_REQUEST_ID
    requestId = ret.getheader(X_CNC_REQUEST_ID)
   
    xmlString = ret.read().decode("utf-8")
    logging.debug("response:" + xmlString)
    doc = minidom.parseString(xmlString)
    purgeListNode = util.getChildNode(doc, 'purge-list')
    purgeList = []
    purgeDataList = util.getChildNodeList(purgeListNode, 'purge-request')
    for purgeNode in purgeDataList:
        purgeId = util.getChildNodeText(purgeNode, 'purge-id')
        requestDateStr = util.getChildNodeText(purgeNode, 'request-date')
        requestDate = util.parseRFC1123Time(requestDateStr)
        itemNodeList = util.getChildNodeList(purgeNode, 'item')
        purgeItems = []
        for itemNode in itemNodeList:
            path = util.getChildNodeText(itemNode, "path")
            status = util.getChildNodeText(itemNode, "status")
            rate = util.getChildNodeText(itemNode, "rate")
            isDir = util.getChildNodeText(itemNode, "isdir")
            purgeItem = PurgeItem(path, status, rate, isDir)
            purgeItems.append(purgeItem)
        purge = Purge(purgeId, requestDate, purgeItems)
        purgeList.append(purge)
    return PurgeQueryResult(ret.status, 'OK', xCncRequestId = requestId, purgeList = purgeList);

def purgeQueryByPurgeIdXmlToPurgeList(ret, purgeId):
    ''' 根据purgeId 缓存查询 xml结果解析成 Purge对象'''
    global X_CNC_REQUEST_ID
    requestId = ret.getheader(X_CNC_REQUEST_ID)
   
    xmlString = ret.read().decode("utf-8")
    logging.debug("response:" + xmlString)
    doc = minidom.parseString(xmlString)
    purgeResultNode = util.getChildNode(doc, 'Result')
    requestDateStr = util.getChildNodeText(purgeResultNode, 'request-date')
    if requestDateStr is not None:
        requestDate = util.parseRFC1123Time(requestDateStr)
    else:
        requestDate = None
    purgeItems = [] # 帝联只有一个item, 就是把所有的url都放在Path里
    purgeList = []
    path = util.getChildNodeText(purgeResultNode, "Path")
    status = util.getChildNodeText(purgeResultNode, "Status")
    rate = util.getChildNodeText(purgeResultNode, "Rate")
    purgeItem = PurgeItem(path, status, rate)
    purgeItems.append(purgeItem)
    purge = Purge(purgeId, requestDate, purgeItems)
    purgeList.append(purge)
    return PurgeQueryResult(ret.status, 'OK', xCncRequestId = requestId, purgeList = purgeList);

def purgeBatchForOneDomainToXml(purgeBatch):
    doc = dom.getDOMImplementation().createDocument('', 'purge-paths', '')
    purgeRootNode = util.getChildNode(doc, 'purge-paths')
    util.addElement(doc, purgeRootNode, 'version', "1.0.0")
    urls = purgeBatch.urls
    if urls is not None and len(urls) > 0 :
        for url in urls:
            util.addElement(doc, purgeRootNode, 'file-path', url)
    dirs = purgeBatch.dirs
    if dirs is not None and len(dirs) > 0:
        for dirItem in dirs:
            util.addElement(doc, purgeRootNode, "dir-path", dirItem)
    return doc.toprettyxml(indent = "", newl="", encoding = 'utf-8');    

    
def purgeBatchToXml(purgeBatch):
    ''' PurgeBatch 对象 转换成 xml '''
    doc = dom.getDOMImplementation().createDocument('', 'purge-urls', '')
    purgeRootNode = util.getChildNode(doc, 'purge-urls')
    util.addElement(doc, purgeRootNode, 'version', "1.0.0")
    urls = purgeBatch.urls
    if urls is not None and len(urls) > 0:
        for url in urls:
            util.addElement(doc, purgeRootNode, 'file-url', url)
    dirs = purgeBatch.dirs
    if dirs is not None and len(dirs) > 0:
        for dirItem in dirs:
            util.addElement(doc, purgeRootNode, "dir-url", dirItem)
    return doc.toprettyxml(indent = "", newl="", encoding = 'utf-8')
