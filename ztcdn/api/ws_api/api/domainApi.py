from __future__ import division
# -*- coding: utf-8 -*-
'''
Created on 2013-1-10

@author: sinlangxmu@gmail.com
@version: 1.0
'''

import sys, ztcdn.api.ws_api.util.ApiUtil as util, xml.dom as dom, xml.dom.minidom as minidom
import traceback, base64
from ztcdn.api.ws_api.util.ApiUtil import BaseResult
from ztcdn.config import WS_USER, WS_PASS
from ztcdn.config import logging
import datetime
import re

logger = logging.getLogger(__name__)

X_CNC_REQUEST_ID = 'x-cnc-request-id'
X_CNC_DATE = 'x-cnc-date'
X_CNC_LOCATION = 'location'
X_CNC_CNAME = 'cname'

REPORT_TYPE_5_MINUTES = 'fiveminutes'
REPORT_TYPE_HOURLY = 'hourly'
REPORT_TYPE_DAILY = 'daily'

class DomainApi(object):
    ''' 域名操作API '''
    HOST = 'http://cloudcdn.chinanetcenter.com';
    #HOST = 'http://192.168.27.161:8080/cloudcdn'
    #HOST = 'http://localhost:8080/cloud-cdn'
    ''' api服务地址 '''

    def __init__(self):
        ''' 
                    初始化DomainApi 用于域名管理相关调用
        @type user: str
        @param user: 用户名
        @type apiKey: str
        @param apiKey: 用户的api key
        @rtype: DomainApi对象
        @return: instance of DomainApi
        '''
        self.user = WS_USER
        self.apiKey = WS_PASS
        self.headers = {'Accept' : 'application/xml', 'Content-Type' : 'application/xml'}
    
    def add(self, domain):
        ''' 创建加速域名 
        @param domain:  新增加速域名构建的Domain对象实例
        @rtype: ProcessResult对象
        @return: 通过ProcessResult.getLocation()新域名的url
        '''
        url = self.HOST + "/api/domain"
        try:
            post = domainToXml(domain)
            logger.debug('request: ' + post)
            ret = util.httpReqeust(url, post, self.makeHeaders(), "POST")
            if ret.status == 202:
                result = xmlToSuccess(ret)
                domainId = result.getLocation().split('/')[-1]
                return self.find(domainId)
            else:
                return xmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))
    
    def listAll(self):
        ''' 获取加速所有域名列表
        @rtype: ProcessResult对象 
        @return: 通过ProcessResult.getDomainSummarys()获取DomainSummary对象的实例列表
        '''
        
        url = self.HOST + "/api/domain"
        try:
            post = ''
            ret = util.httpReqeust(url, post, self.makeHeaders(), "GET")
            if ret.status == 200:
                return xmlToDomainList(ret)
            else:
                return xmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))
        pass
    
    def find(self, domainId):
        ''' 获取加速域名配置  
        @type domainId: str
        @param domainId : 指定查找的域名ID
        @rtype: ProcessResult对象
        @return: 通过ProcessResult.getDomain()返回指定的域名信息的Domain实例
        '''
        
        url = self.HOST + "/api/domain/" + str(domainId)
        try:
            post = ''
            ret = util.httpReqeust(url, post, self.makeHeaders(), "GET")
            if ret.status == 200:
                return xmlToDomain(ret)
            else:
                return xmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))
        pass

    def modify(self, domain):
        ''' 修改加速域名配置 
        @type domain: Domain
        @param domain : 构建需要修改的域名的Domain实例, domain中必须设置domanId字段
        @rtype: ProcessResult对象
        @return: 返回ProcessResult对象
        '''
        
        if domain.domainId is None:
            raise '请设置domainId字段'
        domain.domainName = None  # 清空域名，因为modify不允许修改域名
        url = self.HOST + "/api/domain/" + str(domain.domainId)
        try:
            post = domainToXml(domain)
            #print post
            ret = util.httpReqeust(url, post, self.makeHeaders(), "PUT")
            if ret.status == 202:
                msg = util.getReturnXmlMsg(ret)
                return ProcessResult(0, msg)
            else:
                return xmlToFailure(ret)   
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))
        pass
    
    def delete(self, domainId):
        ''' 删除加速域名 
        @param domainId : 指定待删除的域名ID
        @rtype: ProcessResult对象
        @return: 返回ProcessResult对象
        '''
        
        url = self.HOST + "/api/domain/" + str(domainId)
        try:
            post = ''
            ret = util.httpReqeust(url, post, self.makeHeaders(), "DELETE")
            if ret.status == 202:
                msg = util.getReturnXmlMsg(ret)
                return ProcessResult(0, msg)
            else:
                return xmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))
        pass
    
    def disable(self, domainId):
        ''' 禁用加速域名 
        @param domainId : 指定待禁用的域名ID
        @rtype: ProcessResult对象
        @return: 返回ProcessResult对象
        '''
        
        url = self.HOST + "/api/domain/" + str(domainId)
        try:
            post = ''
            ret = util.httpReqeust(url, post, self.makeHeaders(), "DISABLE")
            if ret.status == 202:
                return xmlToSuccess(ret)
            else:
                return xmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))
        pass
    
    def enable(self, domainId):
        ''' 启用加速域名 
        @param domainId : 指定启用的域名ID
        @rtype: ProcessResult对象
        @return: 返回ProcessResult对象
        '''
        
        url = self.HOST + "/api/domain/" + str(domainId)
        try:
            post = ''
            ret = util.httpReqeust(url, post, self.makeHeaders(), "ENABLE")
            if ret.status == 202:
                return xmlToSuccess(ret)
            else:
                return xmlToFailure(ret) 
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))
        pass

    def purgeQueryByPurgeId(self, purgeId):
        ''' 根据purgeId 查询 缓存记录
        @param purgeId: 缓存id
        @rtype: PurgeQueryResult
        @return: 返回PurgeQueryResult结果,可以 通过PurgeQueryResult.getPurgeList()获取purge记录条目的列表
        '''
        url = self.HOST + "/api/purge/" + str(purgeId)
        try:
            ret = util.httpReqeust(url, "", self.makeHeaders(), "GET")
            if ret.status == 200:
                return purgeQueryByPurgeIdXmlToPurgeList(0, ret, purgeId)
            else:
                return purgeQueryByPurgeIdXmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return PurgeQueryResult(-1, str(e))

    def purge(self, purgeBatch, domainId = None):
        '''  批量清除缓存
        @param domainId: 如果指定了domainId，http body中的file-path和dir-path仅需要提供文件或者目录的uri，
         不能包括域名名称，路径均需以/开始，如/test/a.html 如果未指定domainId, 均需要提供包括域名在内的完整url地址，
         如http://www.baidu.com/test/a.html
        @type purgeBatch: PurgeBatch
        @param purgeBatch 为 PurgeBatch对象 包含files 和 dirs属性
        @rtype: PurgeResult
        @return: 返回PurgeResult结果, 可以通过PurgeResult.getLocation 获得该次缓存
        '''
        if domainId is not None:
            url = self.HOST + "/api/purge/" + str(domainId)
        else:
            url = self.HOST + '/api/purge'
        try:
            if domainId is not None:
                post = purgeBatchForOneDomainToXml(purgeBatch)
            else:
                post = purgeBatchToXml(purgeBatch)
            ret = util.httpReqeust(url, post, self.makeHeaders(), "POST")
            if ret.status == 202 or ret.status == 200:
                return purgeXmlToSuccess(ret)
            else:
                return purgeXmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file = sys.stdout)
            return PurgeResult(-1, str(e))

    def prefetch(self, purgeBatch):
        url = self.HOST + '/api/prefetch'
        try:
            post = prefetchToXml(purgeBatch)
            ret = util.httpReqeust(url, post, self.makeHeaders(), "POST")
            if ret.status == 202:
                return purgeXmlToSuccess(ret)
            else:
                return purgeXmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file = sys.stdout)
            return PurgeResult(-1, str(e))

    def prefetchQueryByPurgeId(self, purgeId):
        url = self.HOST + "/api/prefetch/" + str(purgeId)
        try:
            ret = util.httpReqeust(url, "", self.makeHeaders(), "GET")
            if ret.status == 200:
                return prefetchQueryByPurgeIdXmlToPurgeList(0, ret, purgeId)
            else:
                return purgeQueryByPurgeIdXmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return PurgeQueryResult(-1, str(e))

    def getFlowReport(self, domainName, start, end):
        ''' 获取某域名流量报表 如果domainId 为None,表示 查汇总信息
        @type reportForm: ReportForm
        @param reportForm:  请求的起止时间和报表粒度
        @rtype: FlowRrocessResult
        @return: 通过FlowProcessResult.getFlowPoints() 获得流量查询结果
        '''
        start = util.getRFC3339Time(start +' 00:00:00').replace('+', '%2B')
        end = util.getRFC3339Time(end + ' 23:59:59').replace('+', '%2B')
        domain_id = util.getDomainIdByName(domainName)
        if not domain_id:
            return FlowProcessResult(0, 'Domain id not found')
        url = self.HOST + "/api/report/" + str(domain_id) + "/flow"
        try:
            url = url + '?datefrom=%s&dateto=%s&type=%s' % (start, end, REPORT_TYPE_DAILY)
            ret = util.httpReqeust(url, "", self.makeHeaders(), "GET")
            if ret.status == 200:
                return xmlToFlowPointList(ret, REPORT_TYPE_DAILY)
            else:
                return getFlowReportXmlToDefaultFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return FlowProcessResult(-1, str(e))

    def getBandWidthReport(self, domainName, start, end):
        ''' 获取某域名带宽报表 如果domainId 为None,表示 查汇总信息
        @type reportForm: ReportForm
        @param reportForm:  请求的起止时间和报表粒度
        @rtype: FlowRrocessResult
        @return: 通过FlowProcessResult.getFlowPoints() 获得流量查询结果
        '''
        start = util.getRFC3339Time(start +' 00:00:00').replace('+', '%2B')
        end = util.getRFC3339Time(end + ' 23:59:59').replace('+', '%2B')
        domain_id = util.getDomainIdByName(domainName)
        if not domain_id:
            return FlowProcessResult(0, 'Domain id not found')
        url = self.HOST + "/api/report/" + str(domain_id) + "/flow"
        try:
            url = url + '?datefrom=%s&dateto=%s&type=%s' % (start, end, REPORT_TYPE_5_MINUTES)
            ret = util.httpReqeust(url, "", self.makeHeaders(), "GET")
            if ret.status == 200:
                return xmlToBandWidthPointList(ret, REPORT_TYPE_5_MINUTES)
            else:
                return getFlowReportXmlToDefaultFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return FlowProcessResult(-1, str(e))


    def getReqStatus(self, reqId):
        url = self.HOST + "/api/request/" + str(reqId)
        try:
            ret = util.httpReqeust(url, "", self.makeHeaders(), "GET")
            if ret.status == 200:
                return ret.read()
            else:
                return None
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return PurgeQueryResult(-1, str(e))


    def makeHeaders(self):
        ''' 组装头部  '''  
        global X_CNC_DATE
        headers = self.headers.copy()
        headers[X_CNC_DATE] = util.getRFCTime()
        key = util.hashPassword(headers[X_CNC_DATE], self.apiKey)
        headers['Authorization'] = "Basic " + base64.standard_b64encode(self.user + ':' + key)
        return headers
    
class Domain(object): 
    '''表示为域名对象'''
    def __init__(self, domainName = None, serviceType = None, etag = None, testUrl = None,
                 domainId = None, comment = None, serviceAreas = None, status = None, enabled = None, cname = None,
                 originConfig = None, queryStringSettings = None, cacheBehaviors = None,
                 visitControlRules = None):
        ''' 初始化域名对象
        @param domainName: 设置域名名称
        @param serviceType: 服务类型,默认为web
        @param domainId: 指定域名id，修改域名时使用
        @param comment: 注释
        @param serviceAreas: 加速区域
        @param cname: 获取域名cname信息，只有将域名的dns解析cname到该地址后，流量才会导入到网宿cdn中
        @param status: 查询域名部署状态
        @param enabled: 查询域名是否启用
        @type originConfig: OriginConfig
        @param originConfig: 设置回源信息
        @type cacheBehaviors: list of CacheBehavior
        @param cacheBehaviors: 缓存规则列表, CacheBehavior对象实例的列表
        @type visitControlRules: list of VisitControlRule
        @param visitControlRules: 访问者控制规则列表, VisitControlRule对象实例的列表
        @rtype: Domain  
        '''
        self.domainName = domainName
        self.serviceType = serviceType
        self.etag = etag
        self.testUrl = testUrl
        self.domainId = domainId
        self.comment = comment
        self.serviceAreas = serviceAreas
        self.status = status
        self.enabled = enabled
        self.cname = cname
        self.originConfig = originConfig
        self.queryStringSettings = queryStringSettings
        self.cacheBehaviors = cacheBehaviors
        self.visitControlRules = visitControlRules

class QueryStringSetting(object):
    '''查询串控制'''
    def __init__(self, pathPattern = None, ignoreQueryString = None):
        '''初始化一个查询串控制规则
        @param pathPattern: 设置文件类型，支持多个文件类型,当有多个文件类型时，以,分割
        @type ignoreQueryString: True or False  
        '''
        self.pathPattern = pathPattern
        self.ignoreQueryString = ignoreQueryString

class VisitControlRule(object):
    '''访问者控制规则'''
    def __init__(self, pathPattern = '', allowNullReferer = '', validReferers = '', invalidReferers = '', forbiddenIps = ''):
        '''初始化一个访问者控制规则
        @param pathPattern: 设置文件类型，支持多个文件类型,当有多个文件类型时，以,分割
        @type validReferers: list of str
        @param allowNullReferer: 允许请求referer为空?
        @type allowNullReferer: True or False  
        @param validReferers: referer白名单列表，支持泛域名（如.chinanetcenter.com）
        @type invalidReferers: list of str
        @param invalidReferers: referer黑名单列表，支持泛域名（如.chinanetcenter.com） 
        @type forbiddenIps: list of str
        @param forbiddenIps: ip黑名单列表
        '''
        self.pathPattern = pathPattern
        self.allowNullReferer = allowNullReferer
        self.validReferers = validReferers
        self.invalidReferers = invalidReferers
        self.forbiddenIps = forbiddenIps

class OriginConfig(object):
    ''' 回源配置'''
    
    def __init__(self, originIps = None, originDomainName = None, advOriginConfigs = None):
        ''' 初始化回源配置
        @type originIps: list of str
        @param originIps: 回源ip列表，平台支持多个回源ip
        @param originDomainName: 设置回源域名，平台支持通过ip或者域名回源，但二者只能选一，不能同时提供
        @type advOriginConfigs: list of AdvOriginConfig
        @param advOriginConfigs: 复杂回源规则列表
        '''
        self.originIps = originIps
        self.originDomainName = originDomainName
        self.advOriginConfigs = advOriginConfigs
        
    
class AdvOriginConfig(object):
    '''复杂回源规则'''
    def __init__(self, isps = '', masterIps = '', backupIps = '', detectUrl = '', detectPeriod = ''):
        ''' 初始化复杂回源规则
        @type isps: list of str
        @param isps: 设置isp信息,允许设定多个运营商;dx("中国电信"), wt("中国联通"), yidong("中国移动"), tt("中国铁通"), jyw("中国教育网"), changkuan("长城宽带"), gd("中国广电"), qita("其他"), all("全部");
        @type masterIps: list of str
        @param masterIps: 允许设定多个主IP
        @type backupIps: list of str
        @param backupIps: 允许设定多个备用IP，只有当主IP不可用时，才使用备IP
        @param detectUrl: 监控URL，用于判断源主机是否可用
        @param detectPeriod: 回源监控的频率，单位为S
        '''
        self.isps = isps
        self.masterIps = masterIps
        self.backupIps = backupIps
        self.detectUrl = detectUrl
        self.detectPeriod = detectPeriod

class CacheBehavior(object):
    ''' 缓存行为 '''
    
    def __init__(self, pathPattern = None, ignoreCacheControl = None, cacheTtl = None):
        '''
        @type priority: int
        @param pathPattern: 设置路径匹配格式，支持*通配符以及|、()等正则字符，举例如下： 所有jpg文件：*.jpg 所有jpg或者gif文件：*.(jpg|gif) a/b/c下所有文件：a/b/c/ a/b/c下的所有jpg或者gif文件：a/b/c/*.(jpg|gif)
        @type ignoreCacheControl: boolean
        @param ignoreCacheControl: 设置是否忽略http头中的cache-control
        @param cacheTtl: 设置缓存时间，单位为s 
        '''
        self.pathPattern = pathPattern
        self.ignoreCacheControl = ignoreCacheControl
        self.cacheTtl = cacheTtl

def parseAdvOriginConfigList(nodeList):
    advOriginConfigList = []
    for advOriginConfigNode in nodeList:
        ispsList = util.getChildNodeText(advOriginConfigNode, 'isp')
        masterIpsList = util.getChildNodeText(advOriginConfigNode, 'master-ips')
        backupIpsList = util.getChildNodeText(advOriginConfigNode, 'backup-ips')
        detectUrl = util.getChildNodeText(advOriginConfigNode, 'detect-url')
        detectPeriod = util.getChildNodeText(advOriginConfigNode, 'detect-period')
        isps = splitStr(ispsList)
        masterIps = splitStr(masterIpsList)
        backupIps = splitStr(backupIpsList)
        advOriginConfig = AdvOriginConfig(isps = isps, masterIps = masterIps, backupIps = backupIps, 
                                          detectUrl = detectUrl, detectPeriod = detectPeriod)
        advOriginConfigList.append(advOriginConfig)
    return advOriginConfigList


def parseQueryStringSettingListNode(nodeList):
    queryStringSettingList = []
    for queryStringSetting in nodeList:
        pathPattern = util.getChildNodeText(queryStringSetting, 'path-pattern')
        ignoreQueryStringStr = util.getChildNodeText(queryStringSetting, 'ignore-query-string')
        if ignoreQueryStringStr == "false":
            ignoreQueryString = False
        else:
            ignoreQueryString = True 
        queryStringSetting = QueryStringSetting(pathPattern, ignoreQueryString)
        queryStringSettingList.append(queryStringSetting)
    return queryStringSettingList


def parseCacheBehaviorList(nodeList):
    cacheBehaviorList = []
    for cacheBehavior in nodeList:
        pathPattern = util.getChildNodeText(cacheBehavior, 'path-pattern')
        priority = util.getChildNodeText(cacheBehavior, 'priority')
        ignoreCacheControlStr = util.getChildNodeText(cacheBehavior, 'ignore-cache-control')
        if ignoreCacheControlStr == "false":
            ignoreCacheControl = "False"
        else:
            ignoreCacheControl = "True"
        cacheTTL = util.getChildNodeText(cacheBehavior, 'cache-ttl')
        cacheBehavior = CacheBehavior(pathPattern, ignoreCacheControl, cacheTTL)
        cacheBehaviorList.append(cacheBehavior)
    return cacheBehaviorList

def parseVisitControlRulesList(nodeList):
    vistControlRulesList = []
    for node in nodeList:
        pathPattern = util.getChildNodeText(node, 'path-pattern')
        allowNullReffer = util.getChildNodeText(node, 'allownullreferer')
        validReferRootNode = util.getChildNode(node, "valid-referers")
        validRNode = util.getChildNodeList(validReferRootNode, 'referer')
        validRefers = []
        for ref in validRNode:
            validRefers.append(util.getChildNodeText(ref, "referer"))
        
        invalidReferRootNode = util.getChildNode(node, "invalid-referers")
        invalidRNode = util.getChildNodeList(invalidReferRootNode, 'referer')
        invalidRefers = []
        for ref in invalidRNode:
            invalidRefers.append(util.getChildNodeText(ref, "referer"))
        
        forbiddenIps = splitStr(util.getChildNodeText(node, 'forbidden-ips'))
        
        visitControlRule = VisitControlRule(pathPattern, allowNullReffer, validRefers, invalidRefers, forbiddenIps)
        vistControlRulesList.append(visitControlRule)
        
    return vistControlRulesList

def splitStr(data):
    list1 = data.split(";")
    res = []
    for item in list1:
        res = item.split(",") + res
    return res

def xmlToDomain(ret):
    ''' 返回xml 转换成 带 Domain对象的ProcessResult对象, 在查询频道信息的时候使用'''
    
    global X_CNC_REQUEST_ID, X_CNC_LOCATION, logger
    requestId = ret.getheader(X_CNC_REQUEST_ID)
    
    xmlString = ret.read().decode("utf-8")
    logger.debug("response:" + xmlString)
    logger.debug("response: Request_id => " + requestId)
    doc = minidom.parseString(xmlString)
    
    domainNode = util.getChildNode(doc, 'domain')
    domainName = util.getChildNodeText(domainNode, 'domain-name')
    domainId = util.getChildNodeText(domainNode, 'domain-id')
    serviceType = util.getChildNodeText(domainNode, 'service-type')
    comment = util.getChildNodeText(domainNode, 'comment')
    serviceAreas = util.getChildNodeText(domainNode, 'service-areas')
    enabled = util.getChildNodeText(domainNode, 'enabled')
    cname = util.getChildNodeText(domainNode, 'cname')
    status = util.getChildNodeText(domainNode, 'status')
    
    domain = Domain(domainName = domainName, 
                    serviceType = serviceType, 
                    domainId = domainId,
                    comment = comment, 
                    serviceAreas = serviceAreas,
                    enabled = enabled, 
                    cname = cname,
                    status = status)
    
    originConfigNode = util.getChildNode(domainNode, 'origin-config')
    if originConfigNode is not None:
        originIpsStr = util.getChildNodeText(originConfigNode, 'origin-ips')
        originIps = splitStr(originIpsStr)
        originDomainName = util.getChildNodeText(originConfigNode, 'origin-domain-name')
        advOriginConfigListRootNode = util.getChildNode(originConfigNode, 'adv-origin-configs')
        if advOriginConfigListRootNode is not None:
            advOriginConfigListNode = util.getChildNodeList(advOriginConfigListRootNode, 'adv-origin-config')
            advOriginConfigs = []
            if advOriginConfigListNode is not None:
                advOriginConfigs = parseAdvOriginConfigList(advOriginConfigListNode)
                originConfig = OriginConfig(originIps, originDomainName, advOriginConfigs)
                domain.originConfig = originConfig   
        else:
            originConfig = OriginConfig(originIps, originDomainName)
            domain.originConfig = originConfig   
    
    queryStringSettingListRootNode = util.getChildNode(domainNode, 'query-string-settings')
    if queryStringSettingListRootNode is not None:
        queryStringSettingListNode = util.getChildNodeList(queryStringSettingListRootNode, 'query-string-setting')
        if queryStringSettingListNode is not None:
            queryStringSettingList = parseQueryStringSettingListNode(queryStringSettingListNode)
            domain.queryStringSettings = queryStringSettingList
    
    cacheBehaviorListRootNode = util.getChildNode(domainNode, 'cache-behaviors')
    if cacheBehaviorListRootNode is not None:
        cacheBehaviorListNode = util.getChildNodeList(cacheBehaviorListRootNode, 'cache-behavior')
        if cacheBehaviorListNode is not None:
            cacheBehaviorList = parseCacheBehaviorList(cacheBehaviorListNode)
            domain.cacheBehaviors = cacheBehaviorList
    
    visitControlRulesListRootNode = util.getChildNode(domainNode, 'visit-control-rules')
    if visitControlRulesListRootNode is not None:
        visitControlRulesListNode = util.getChildNodeList(visitControlRulesListRootNode, 'visit-control-rule')
        if visitControlRulesListNode is not None:
            visitControlRulesList = parseVisitControlRulesList(visitControlRulesListNode)
            domain.visitControlRules = visitControlRulesList
        
    return ProcessResult(0, 'OK', xCncRequestId = requestId, domain = domain);

def domainToXml(domain):
    ''' Domain 对象 转换成 xml '''
    
    doc = dom.getDOMImplementation().createDocument('', 'domain', '')
    domainNode = util.getChildNode(doc, 'domain')
    util.addElement(doc, domainNode, 'version', "1.0.0")
    if domain.domainName is not None:
        util.addElement(doc, domainNode, 'domain-name',  domain.domainName)
    if domain.serviceType is not None:
        util.addElement(doc, domainNode, 'service-type',  domain.serviceType)
    if domain.comment is not None:
        util.addElement(doc, domainNode, 'comment',  domain.comment)
    if domain.cname is not None:
        util.addElement(doc, domainNode, 'cname',  domain.cname)
    if domain.status is not None:
        util.addElement(doc,domainNode, 'status', domain.status)
    #if domain.domainId is not None:
        #util.addElement(doc, domainNode, 'domain-id', domain.domainId)
    
    if domain.serviceAreas is not None:
        util.addElement(doc, domainNode, 'service-areas', domain.serviceAreas)
    else:
        util.addElement(doc, domainNode, 'service-areas', 'cn')
    
    if domain.originConfig is not None:
        originConfigNode = util.addElement(doc, domainNode, 'origin-config')
        if domain.originConfig.originIps is not None:
            originIps = domain.originConfig.originIps
            util.addElement(doc, originConfigNode, 'origin-ips', ';'.join(originIps))
        if domain.originConfig.originDomainName is not None:
            util.addElement(doc, originConfigNode, 'origin-domain-name', domain.originConfig.originDomainName)
        if domain.originConfig.advOriginConfigs is not None:
            advOriginConfigsNode = util.addElement(doc, originConfigNode, 'adv-origin-configs')
            for advOriginConfig in domain.originConfig.advOriginConfigs:
                isps = advOriginConfig.isps
                advOriginConfigNode = util.addElement(doc, advOriginConfigsNode, 'adv-origin-config')
                util.addElement(doc, advOriginConfigNode, 'isp', ';'.join(isps))
                util.addElement(doc, advOriginConfigNode, 'master-ips', ';'.join(advOriginConfig.masterIps))
                util.addElement(doc, advOriginConfigNode, 'backup-ips', ';'.join(advOriginConfig.backupIps))
                util.addElement(doc, advOriginConfigNode, 'detect-url', advOriginConfig.detectUrl)
                util.addElement(doc, advOriginConfigNode, 'detect-period', advOriginConfig.detectPeriod)                
    
    if domain.queryStringSettings is not None:
        queryStringSettingsNode = util.addElement(doc, domainNode, 'query-string-settings')
        for queryStringSetting in domain.queryStringSettings:
            queryStringSettingNode = util.addElement(doc, queryStringSettingsNode, 'query-string-setting')
            util.addElement(doc, queryStringSettingNode, 'path-pattern', queryStringSetting.pathPattern)
            if queryStringSetting.ignoreQueryString == False:
                util.addElement(doc, queryStringSettingNode, 'ignore-query-string', "false")
            else:
                util.addElement(doc, queryStringSettingNode, 'ignore-query-string', "true")
    
    if domain.cacheBehaviors is not None:
        cacheBehaviorsNode = util.addElement(doc, domainNode, 'cache-behaviors')
        for cacheBehavior in domain.cacheBehaviors:
            cacheBehaviorNode = util.addElement(doc, cacheBehaviorsNode, 'cache-behavior')
            util.addElement(doc, cacheBehaviorNode, 'path-pattern', cacheBehavior.pathPattern)
            if cacheBehavior.ignoreCacheControl == "False":
                util.addElement(doc, cacheBehaviorNode, 'ignore-cache-control', "false")
            else:
                util.addElement(doc, cacheBehaviorNode, 'ignore-cache-control', "true")
            util.addElement(doc, cacheBehaviorNode, 'cache-ttl', cacheBehavior.cacheTtl)
    
    if domain.visitControlRules is not None:
        visitControlRulesNode = util.addElement(doc, domainNode, 'visit-control-rules')
        for visitControl in domain.visitControlRules:
            visitControlNode = util.addElement(doc, visitControlRulesNode, "visit-control-rule")
            if visitControl.allowNullReferer == True:
                util.addElement(doc, visitControlNode, 'allownullreferer', "true")
            elif visitControl.allowNullReferer == False:
                util.addElement(doc, visitControlNode, 'allownullreferer', "false")
            
            util.addElement(doc, visitControlNode, 'path-pattern', visitControl.pathPattern)
            validRNode = util.addElement(doc, visitControlNode, 'valid-referers')
            validReferers = visitControl.validReferers
            if validReferers is not None and len(validReferers) > 0 :
                for referer in validReferers:
                    util.addElement(doc, validRNode, 'referer', referer)
            invalidRNode = util.addElement(doc, visitControlNode, 'invalid-referers')
            invalidReferers = visitControl.invalidReferers
            if invalidReferers is not None and len(invalidReferers) > 0 :
                for referer in invalidReferers:
                    util.addElement(doc, invalidRNode, 'referer', referer)
            util.addElement(doc, visitControlNode, 'forbidden-ips', ';'.join(visitControl.forbiddenIps))
    return doc.toprettyxml(indent = "", newl="", encoding = 'utf-8')

def xmlToDomainList(ret):
    ''' 返回xml 转换成 带 Domain对象列表的ProcessResult对象, 在查询用户下所有频道时候使用'''
    global X_CNC_REQUEST_ID, X_CNC_LOCATION
    requestId = ret.getheader(X_CNC_REQUEST_ID)
    
    xmlString = ret.read().decode("utf-8")
    logger.debug("response:" + xmlString)
    doc = minidom.parseString(xmlString)
    domainListNode = util.getChildNode(doc, 'domain-list')
    domainList = []
    domainSummaryList = util.getChildNodeList(domainListNode, 'domain-summary')
    for domainNode in domainSummaryList:
        domainId = util.getChildNodeText(domainNode, 'domain-id')
        cname = util.getChildNodeText(domainNode, 'cname')
        domainName = util.getChildNodeText(domainNode, 'domain-name')
        status = util.getChildNodeText(domainNode, 'status')
        serviceType = util.getChildNodeText(domainNode, "service-type")
        enabled = util.getChildNodeText(domainNode, 'enabled')== 'true'
        cdnServiceStatus = util.getChildNodeText(domainNode, 'cdn-service-status') == 'true'
        domainSummary = DomainSummary(domainId, domainName, cname,
                  status, enabled,
                  serviceType, cdnServiceStatus)
        domainList.append(domainSummary)
    return ProcessResult(0, 'OK', xCncRequestId = requestId, domainSummarys = domainList);

class DomainSummary(object):
    ''' 查询域名列表 返回 的列表中 单个域名的信息 '''
    def __init__(self, domainId = None, domainName = None, cname = None,
                  status = None, enabled = None,
                  serviceType = None, cdnServiceStatus = None):
        '''
        @param domainName: 设置域名名称
        @param serviceType: 服务类型
        @param domainId: 指定域名id，修改域名时使用
        @param cname: 获取域名cname信息，只有将域名的dns解析cname到该地址后，流量才会导入到网宿cdn中
        @param cdnServiceStatus: 域名服务状态
        @param status: 查询域名部署状态
        @param enabled: 查询域名是否启用
        '''
        self.domainId = domainId
        self.domainName = domainName
        self.cname = cname
        self.status = status
        self.enabled = enabled
        self.serviceType = serviceType
        self.cdnServiceStatus = cdnServiceStatus
        
class ProcessResult(BaseResult):
    '''表示请求的返回结果'''
    def __init__(self, ret, msg, xCncRequestId = None, domain = None, domainSummarys = None, location = None,
                 cname = None):
        '''
        @param ret: HTTP响应状态码
        @param msg: 响应消息
        @param xCncRequestId: 每一次请求，都会被分配一个唯一的id
        @param domain: 查询域名 返回的域名Domain实例
        @type domainSummarys: list of DomainSummary
        @param domainSummarys:  查询域名列表,返回的 域名基本信息 列表
        @param location: 返回新域名的url, 只有新增域名时候才有, 
        @param cname: 返回新域名的cname
        '''
        super(ProcessResult, self).__init__(ret, msg, xCncRequestId)
        self.domainSummarys = domainSummarys
        self.location = location
        self.domain = domain
        self.cname = cname
    
    def getDomainSummarys(self):
        ''' 如果返回多个域名信息, 调用此方法获取'''
        return self.domainSummarys
    
    def getDomain(self):
        ''' 如果返回含有单个域名信息, 调用此方法获取'''
        return self.domain
   
    def getLocation(self):
        ''' 返回频道的location信息, 只有新增频道时候才有'''
        return self.location
    
    def getCname(self):
        ''' 返回频道的cname信息'''
        return self.cname
        
def xmlToSuccess(ret):
    ''' 返回xml 转换成 成功返回的ProcessResult对象'''
    global X_CNC_REQUEST_ID, X_CNC_LOCATION, X_CNC_CNAME
    requestId = ret.getheader(X_CNC_REQUEST_ID)
    location = ret.getheader(X_CNC_LOCATION)
    cname = ret.getheader(X_CNC_CNAME)
    msg = util.getReturnXmlMsg(ret)
    return ProcessResult(ret.status, msg, xCncRequestId = requestId, location = location, cname = cname)
     
def xmlToFailure(ret):
    msg = util.getReturnXmlMsg(ret)
    return ProcessResult(ret.status, ret.reason + ":" + msg)

####### purgeApi ##########
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
    def __init__(self, url = None, status = None, rate = None, isdir = None, itemId = None):
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
        self.itemId = itemId

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
    msg = util.getReturnXmlMsg(ret)
    if ret.status == 202:
        status = 0
    else:
        status = ret.status
    return PurgeResult(status, msg, xCncRequestId = requestId, location = location)

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
    logger.debug("response:" + xmlString)
    logger.debug("response: Request_id => " + requestId)
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

def purgeQueryByPurgeIdXmlToPurgeList(ret_status, ret, purgeId):
    ''' 根据purgeId 缓存查询 xml结果解析成 Purge对象'''
    global X_CNC_REQUEST_ID
    requestId = ret.getheader(X_CNC_REQUEST_ID)

    xmlString = ret.read().decode("utf-8")
    logger.debug("response:" + xmlString)
    logger.debug("response: Request_id => " + requestId)
    doc = minidom.parseString(xmlString)
    purgeResultNode = util.getChildNode(doc, 'purge-result')
    requestDateStr = util.getChildNodeText(purgeResultNode, 'request-date')
    if requestDateStr is not None:
        requestDate = util.parseRFC1123Time(requestDateStr)
    else:
        requestDate = None
    itemNodeList = util.getChildNodeList(purgeResultNode, 'item')
    purgeItems = []
    purgeList = []
    for itemNode in itemNodeList:
        path = util.getChildNodeText(itemNode, "path")
        status = util.getChildNodeText(itemNode, "status")
        rate = util.getChildNodeText(itemNode, "rate")
        isDir = util.getChildNodeText(itemNode, "isdir")
        purgeItem = PurgeItem(path, status, rate, isDir)
        purgeItems.append(purgeItem)

    # 由于帝联只返回一个结果，所以要合并成一个
    pathList = []
    statusList = []
    rateTotal = 0
    purgeItems1 = []
    for p in purgeItems:
        pathList.append(p.url)
        statusList.append(p.status)
        rateTotal += float(p.rate)
    path = ','.join(pathList)
    if "run" in statusList:
        status = "run"
    elif "wait" in statusList:
        status = "wait"
    elif "failure" in statusList:
        status = "failure"
    else:
        status = "success"
    rate = round(rateTotal/len(purgeItems),2)
    purgeItem1 = PurgeItem(path, status, str(rate))
    purgeItems1.append(purgeItem1)

    purge = Purge(purgeId, requestDate, purgeItems1)
    purgeList.append(purge)
    return PurgeQueryResult(ret_status, 'OK', xCncRequestId = requestId, purgeList = purgeList)

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
    return doc.toprettyxml(indent = "", newl="", encoding = 'utf-8')


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

def prefetchToXml(purgeBatch):
    ''' PurgeBatch 对象 转换成 用来预缓存的xml '''
    doc = dom.getDOMImplementation().createDocument('', 'prefetch-urls', '')
    purgeRootNode = util.getChildNode(doc, 'prefetch-urls')
    util.addElement(doc, purgeRootNode, 'version', "1.0.0")
    urls = purgeBatch.urls
    if urls is not None and len(urls) > 0:
        for url in urls:
            util.addElement(doc, purgeRootNode, 'prefetch-url', url)
    dirs = purgeBatch.dirs
    if dirs is not None and len(dirs) > 0:
        for dirItem in dirs:
            util.addElement(doc, purgeRootNode, "prefetch-url", dirItem)
    return doc.toprettyxml(indent = "", newl="", encoding = 'utf-8')

def prefetchQueryByPurgeIdXmlToPurgeList(ret_status, ret, purgeId):
    ''' 根据purgeId 缓存查询 xml结果解析成 Purge对象'''
    global X_CNC_REQUEST_ID
    requestId = ret.getheader(X_CNC_REQUEST_ID)

    xmlString = ret.read().decode("utf-8")
    logger.debug("response:" + xmlString)
    logger.debug("response: Request_id => " + requestId)
    doc = minidom.parseString(xmlString)
    purgeResultNode = util.getChildNode(doc, 'prefetch-result')
    requestDateStr = util.getChildNodeText(purgeResultNode, 'request-date')
    if requestDateStr is not None:
        requestDate = util.parseRFC1123Time(requestDateStr)
    else:
        requestDate = None
    itemsNodeList = util.getChildNode(purgeResultNode, 'items')
    itemNodeList = util.getChildNodeList(itemsNodeList, 'item')
    purgeItems = []
    purgeList = []
    for itemNode in itemNodeList:
        path = util.getChildNodeText(itemNode, "path")
        status = util.getChildNodeText(itemNode, "status")
        rate = util.getChildNodeText(itemNode, "rate")
        itemId = util.getChildNodeText(itemNode, "itemId")
        purgeItem = PurgeItem(url=path, status=status, rate=rate, itemId = itemId)
        purgeItems.append(purgeItem)
    purge = Purge(purgeId, requestDate, purgeItems)
    purgeList.append(purge)
    return PurgeQueryResult(ret_status, 'OK', xCncRequestId = requestId, purgeList = purgeList)

# 以下为流量
# 为查询流量增加 params
def appendParams(url, reportForm):
    dateFrom = reportForm.getDateFrom()
    dateTo = reportForm.getDateTo()
    reportType = reportForm.getReportType()
    originUrl = url + "?"
    if dateFrom or dateTo or type:
        url = url + "?"
    if dateFrom:
        url = url + "datefrom=" + util.getRFC3339Time(dateFrom).replace('+', '%2B')
    if dateTo:
        if url == originUrl:
            url = originUrl + "dateto=" + util.getRFC3339Time(dateTo).replace('+', '%2B')
        else:
            url =  url + "&dateto=" + util.getRFC3339Time(dateTo).replace('+', '%2B')
    if reportType:
        if url == originUrl:
            url = originUrl + "type=" + reportType
        else:
            url = url + "&type=" + reportType
    return url

def xmlToFlowPointList(ret, reportType):
    ''' 返回xml 转换成 带 FlowPoint对象列表的FlowProcessResult对象'''
    global X_CNC_REQUEST_ID, X_CNC_LOCATION
    requestId = ret.getheader(X_CNC_REQUEST_ID)

    isoFormat = getDateFormat(reportType)
    xmlString = ret.read().decode("utf-8")
    logger.debug("response:" + xmlString)
    logger.debug("response: Request_id => " + requestId)
    doc = minidom.parseString(xmlString)
    flowPointListNode = util.getChildNode(doc, 'flow-report')
    flowSummary = util.getChildNodeText(flowPointListNode, 'flow-summary')
    flowPointList = []
    flowDataList = util.getChildNodeList(flowPointListNode, 'flow-data')
    time_delta = datetime.timedelta(seconds=1)
    for flowNode in flowDataList:
        pointStr = util.getChildNodeText(flowNode, 'timestamp')
        if re.search('24:00:00', pointStr):
            # 网宿的0点为24:00:00 ， 改成 00:00:00
            pointStr = pointStr.replace('24:00:00', '23:59:59')
            point = datetime.datetime.strptime(pointStr, isoFormat)
            pointStr = (point + time_delta).strftime(isoFormat)
        # point = datetime.datetime.strptime(pointStr, isoFormat)
        flow = util.getChildNodeText(flowNode, 'flow')
        flowPoint = FlowPoint(pointStr, flow)
        flowPointList.append(flowPoint)
    return FlowProcessResult(0, 'OK', xCncRequestId = requestId,
                             flowPoints = flowPointList, flowSummary = flowSummary)

def xmlToBandWidthPointList(ret, reportType):
    ''' 返回xml 转换成 带 FlowPoint对象列表的FlowProcessResult对象'''
    global X_CNC_REQUEST_ID, X_CNC_LOCATION
    requestId = ret.getheader(X_CNC_REQUEST_ID)

    isoFormat = getDateFormat(reportType)
    xmlString = ret.read().decode("utf-8")
    logger.debug("response:" + xmlString)
    logger.debug("response: Request_id => " + requestId)
    doc = minidom.parseString(xmlString)
    flowPointListNode = util.getChildNode(doc, 'flow-report')
    flowSummary = util.getChildNodeText(flowPointListNode, 'flow-summary')
    flowPointList = []
    flowDataList = util.getChildNodeList(flowPointListNode, 'flow-data')
    time_delta = datetime.timedelta(seconds=1)
    for flowNode in flowDataList:
        pointStr = util.getChildNodeText(flowNode, 'timestamp')
        if re.search('24:00:00', pointStr):
            pointStr = pointStr.replace('24:00:00', '23:59:59')
            point = datetime.datetime.strptime(pointStr, isoFormat)
            pointStr = (point + time_delta).strftime(isoFormat)
        pointStr = pointStr[:16]  # 由于帝联的是2015-12-01 00:10 没有带秒， 所以网宿的删除秒
        flow = util.getChildNodeText(flowNode, 'flow')
        # 网宿没有带宽，所以需要把流量转换成带宽
        bandwidth = round(float(flow) * 8 / 300, 2)
        flowPoint = FlowPoint(pointStr, bandwidth)
        flowPointList.append(flowPoint)
    return FlowProcessResult(0, 'OK', xCncRequestId = requestId,
                             flowPoints = flowPointList, flowSummary = flowSummary)

def getDateFormat(reportType):
    if reportType == REPORT_TYPE_5_MINUTES:
        return "%Y-%m-%d %H:%M:%S"
    elif reportType == REPORT_TYPE_HOURLY:
        return "%Y-%m-%d %H:%M"
    else :
        return "%Y-%m-%d"


class FlowPoint(object):
    '''流量统计结果'''
    def __init__(self, point = None, flow = None):
        '''初始化
        @param point: 流量统计时间点
        @param flow: 流量统计值,单位为M
        '''
        self.point = point
        self.flow = flow

    def getPoint(self):
        return self.point
    def setPoint(self, point):
        self.point = point
    def getFlow(self):
        return self.flow
    def setFlow(self, flow):
        self.flow = flow

class FlowProcessResult(BaseResult):
    '''流量查询结果'''
    def __init__(self, ret, msg, xCncRequestId = None, flowPoints = None, flowSummary = None):
        '''
        @type flowPoints: list of FlowPoint
        @param flowPoints: 返回流量统计结果列表
        '''
        super(FlowProcessResult, self).__init__(ret, msg, xCncRequestId)
        self.flowPoints = flowPoints
        self.flowSummary = flowSummary

    def getFlowPoints(self):
        '''返回流量统计结果列表'''
        return self.flowPoints

def getFlowReportXmlToDefaultFailure(ret):
    msg = util.getReturnXmlMsg(ret)
    return FlowProcessResult(ret.status, ret.reason + ":" + msg)