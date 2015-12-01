#coding:utf8
__author__ = 'liujiahua'
import logging
import httplib
import hashlib
from ztcdn.api.dl_api.util.ApiUtil import BaseResult
import ztcdn.api.dl_api.util.ApiUtil as util
import xml.dom as dom, xml.dom.minidom as minidom
import sys
import traceback
from ztcdn.config import DL_USER, DL_PASS

reload(sys)
sys.setdefaultencoding('utf-8')

logger = logging.getLogger(__name__)

REQ_DICT = {
    "config":{
        "rq_url":"/DnionCloud/distribution/%s/config_update",#distributionID
        "type":"POST",
        "postfile":"y",
    },
    "create":{
        "rq_url":"/DnionCloud/distribution/create",
        "type":"POST",
        "postfile":"y",
    },
    "del":{
        "rq_url":"/DnionCloud/distribution/%s/delete", #distributionID
        "type":"POST",
        "postfile":"n",
    },
    "get":{
        "rq_url":"/DnionCloud/distribution/%s/get", #distributionID
        "type":"GET",
        "postfile":"n",
    },
    "list":{
        "rq_url":"/DnionCloud/distribution/list",
        "type":"GET",
        "postfile":"n",
    },
    "prefetch_progress":{
        "rq_url":"/DnionCloud/cdnPrefetch/progress_old?RequestId=%s", #RequestId
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
    },
    "flowValue":{
        "rq_url":"/DnionCloud/Bandwidth/flowValue?domain=%s&beginDate=%s&endDate=%s",
        #domain & beginDate & endDate & url_escape(province) & url_escape(isp)
        "type":"POST",
        "postfile":"n",
    },
    "bandwidthvalue":{
        "rq_url":"/DnionCloud/Bandwidth/bandwidthValue?domain=%s&date=%s&endDate=%s",#domain&date
        "type":"POST",
        "postfile":"n",
    }
}

X_CNC_REQUEST_ID = 'X-Dnion-Request-Id'
X_CNC_DATE = 'Date'
X_CNC_LOCATION = 'location'
X_CNC_CNAME = 'cname'
X_Dnion_Etag = 'Etag'

REPORT_TYPE_5_MINUTES = 'fiveminutes'
REPORT_TYPE_HOURLY = 'hourly'
REPORT_TYPE_DAILY = 'daily'

class DomainApi(object):
    def __init__(self, domain_name=None, domain_ip=None, test_url=None):
        self.domain_name = domain_name
        self.domain_ip = domain_ip
        self.test_url = test_url
        self.key = DL_USER
        self.credential = DL_PASS

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

    def md5_file(self, name):
        m = hashlib.md5()
        a_file = open(name, 'rb')    #需要使用二进制格式读取文件内容
        m.update(a_file.read())
        a_file.close()
        return m.hexdigest()

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

    def add(self, domain):
        type = REQ_DICT['create']['type']
        rq_url = REQ_DICT['create']['rq_url']
        rq_body = domainToXml(domain)
        print 'DDDDDDD %s' % rq_body
        res = self.req(type, rq_url, rq_body)
        if res.status == 201:
            return xmlToDomain(res)
        else:
            return xmlToFailure(res)

    def listAll(self):
        type = REQ_DICT['list']['type']
        rq_url = REQ_DICT['list']['rq_url']
        rq_body = ''
        res = self.req(type, rq_url, rq_body)
        if res.status == 200:
            return res.read()
        else:
            return xmlToFailure(res)

    def find(self, disId):
        type = REQ_DICT['get']['type']
        rq_url = REQ_DICT['get']['rq_url'] % disId
        rq_body = ''
        res = self.req(type, rq_url, rq_body)
        if res.status == 200:
            return xmlToDomain(res)
        else:
            return xmlToFailure(res)

    def modify(self, domain):
        type = REQ_DICT['config']['type']
        rq_url = REQ_DICT['config']['rq_url'] % domain.domainId
        result = self.find(domain.domainId)
        if result.getRet() == 0:
            d = result.getDomain()
            etag = d.etag
            rq_body = domainToXml(domain)
            print rq_body
            res = self.req(type, rq_url, rq_body, etag)
            if res.status == 200:
                return ProcessResult(0, 'OK')
            else:
                return xmlToFailure(res)
        else:
            print 'cannot find %s' % domain.domainId
            return result

    def delete(self, disId):
        r = self.disable(disId)
        print r.getRet(),r.getMsg()
        result = self.find(disId)
        if result.getRet() == 0:
            domain = result.getDomain()
            etag = domain.etag
            type = REQ_DICT['del']['type']
            rq_url = REQ_DICT['del']['rq_url'] % disId
            rq_body = ''
            res = self.req(type, rq_url, rq_body, etag)
            if res.status == 200:
                return ProcessResult(0, 'OK')
            else:
                return xmlToFailure(res)
        else:
            print 'cannot find %s' % disId
            return result

    def enable(self, disId):
        result = self.find(disId)
        if result.getRet() == 0:
            domain = result.getDomain()
            domain.enabled = True
            etag = domain.etag
            type = REQ_DICT['config']['type']
            rq_url = REQ_DICT['config']['rq_url'] % domain.domainId
            rq_body = domainToXml(domain)
            res = self.req(type, rq_url, rq_body, etag)
            if res.status == 200:
                return xmlToDomain(res)
            else:
                return xmlToFailure(res)
        else:
            return result

    def disable(self, disId):
        result = self.find(disId)
        if result.getRet() == 0:
            domain = result.getDomain()
            domain.enabled = False
            etag = domain.etag
            type = REQ_DICT['config']['type']
            rq_url = REQ_DICT['config']['rq_url'] % domain.domainId
            rq_body = domainToXml(domain)
            res = self.req(type, rq_url, rq_body, etag)
            if res.status == 200:
                return xmlToDomain(res)
            else:
                return xmlToFailure(res)
        else:
            return result

    ########### purgeApi #############
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
                return purgeQueryByPurgeIdXmlToPurgeList(0, ret, purgeId)
            else:
                return purgeQueryByPurgeIdXmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return PurgeQueryResult(-1, str(e))

    def prefetch(self, purgeBatch, domainId = None):
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
        url_list = []
        if purgeBatch.urls is not None:
            url_list = purgeBatch.urls
        if purgeBatch.dirs is not None:
            url_list = purgeBatch.dirs
        url_str = '\n'.join(url_list)
        type = REQ_DICT['prefetch']['type']
        rq_url = REQ_DICT['prefetch']['rq_url']
        rq_body = url_str
        try:
            ret = self.req(type, rq_url, rq_body)
            if ret.status == 200:
                return purgeXmlToSuccess(ret)
            else:
                return purgeXmlToFailure(ret)
        except Exception, e:
            traceback.print_exc(file = sys.stdout)
            return PurgeResult(-1, str(e))


    def prefetchQueryByPurgeId(self, purgeId):
        try:
            type = REQ_DICT['prefetch_progress']['type']
            rq_url = REQ_DICT['prefetch_progress']['rq_url'] % purgeId
            rq_body = ''
            ret = self.req(type, rq_url, rq_body)
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
        try:
            type = REQ_DICT['flowValue']['type']
            rq_url = REQ_DICT['flowValue']['rq_url'] % (domainName, start, end)
            rq_body = ''
            ret = self.req(type, rq_url, rq_body)
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
        try:
            type = REQ_DICT['bandwidthvalue']['type']
            rq_url = REQ_DICT['bandwidthvalue']['rq_url'] % (domainName, start, end)
            rq_body = ''
            ret = self.req(type, rq_url, rq_body)
            if ret.status == 200:
                return xmlToBandWidthPointList(ret, REPORT_TYPE_HOURLY)
            else:
                return getFlowReportXmlToDefaultFailure(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return FlowProcessResult(-1, str(e))

    def logDownload(self, domain_name, date, hour):
        type = REQ_DICT['config']['type']
        rq_url = REQ_DICT['config']['rq_url'] % (domain_name, date, hour)
        rq_body = ''
        response, resp = self.req(type, rq_url, rq_body)
        status = response.status
        reason = response.reason
        logger.info("Download Request Url: %s" % rq_url)
        logger.info("Download status:%s, reason:%s, resp:%s" % (status, reason, resp))
        return (status, reason, resp)


    def prefetchProgress(self, req_id):
        type = REQ_DICT['prefetch_progress']['type']
        rq_url = REQ_DICT['prefetch_progress']['rq_url'] % req_id
        rq_body = ''
        response, resp = self.req(type, rq_url, rq_body)
        status = response.status
        reason = response.reason
        logger.info("PrefetchProgress Request Url: %s" % rq_url)
        logger.info("PrefetchProgress status:%s, req_id: %s, reason:%s, resp:%s" % (status, req_id, reason, resp))
        return (status, reason, resp)

    def bandwidthMap(self, domain_name, start, end):
        type = REQ_DICT['bandwidthvalue']['type']
        rq_url = REQ_DICT['bandwidthvalue']['rq_url'] % (domain_name, start, end)
        rq_body = ''
        response, resp = self.req(type, rq_url, rq_body)
        status = response.status
        reason = response.reason
        logger.info("BankwidthMap Request Url: %s" % rq_url)
        logger.info("BandwidthMap status:%s, reason:%s， resp:%s" % (status, reason, resp))
        return (status, reason, resp)

    def analyticsServer(self, domain_name, start, end, req_type):
        type = REQ_DICT['analyticsServer']['type']
        rq_url = REQ_DICT['analyticsServer']['rq_url'] % (domain_name, start, end, req_type)
        rq_body = ''
        response, resp = self.req(type, rq_url, rq_body)
        status = response.status
        reason = response.reason
        logger.info("AnalyticsServer Request Url: %s" % rq_url)
        logger.info("AnalyticsServer status:%s, reason:%s, resp:%s" % (status, reason, resp))
        return (status, reason, resp)

    def logDownloadList(self, domain_name, start, end):
        type = REQ_DICT['logDownLoadList']['type']
        rq_url = REQ_DICT['logDownLoadList']['rq_url'] % (domain_name, start, end)
        rq_body = ''
        response, resp = self.req(type, rq_url, rq_body)
        status = response.status
        reason = response.reason
        logger.info("LogDownload Request Url: %s" % rq_url)
        logger.info("LogDownload status:%s, reason:%s, resp:%s" % (status, reason, resp))
        return (status, reason, resp)

    def flowValue(self, domain_name, start, end, prov='', isp=''):
        type = REQ_DICT['flowValue']['type']
        rq_url = REQ_DICT['flowValue']['rq_url'] % (domain_name, start, end, prov, isp)
        rq_body = ''
        response, resp = self.req(type, rq_url, rq_body)
        status = response.status
        reason = response.reason
        logger.info("flowValue Request Url: %s" % rq_url)
        logger.info("flowValue status:%s, reason:%s, resp:%s" % (status, reason, resp))
        return (status, reason, resp)

class Domain(object):
    '''表示为域名对象'''
    def __init__(self, domainName = None, serviceType = None, etag = None, testUrl = None,
                 domainId = None, comment = "create", faildComment = None, serviceAreas = None, status = None, enabled = "True", cname = None,
                 originConfig = None, cacheBehaviors = None,
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
        self.testUrl = testUrl
        self.serviceType = serviceType
        self.domainId = domainId
        self.etag = etag
        self.comment = comment
        self.faildComment = faildComment
        self.serviceAreas = serviceAreas
        self.status = status
        self.enabled = enabled
        self.cname = cname
        self.originConfig = originConfig
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
    def __init__(self, pathPattern = None, whiteList = None, blackList = None, denyIpList = None):
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
        self.whiteList = whiteList
        self.blackList = blackList
        self.denyIpList = denyIpList


class OriginConfig(object):
    ''' 回源配置'''

    def __init__(self, originIps = None, advOriginConfigs = None):
        ''' 初始化回源配置
        @type originIps: list of str
        @param originIps: 回源ip列表，平台支持多个回源ip
        @param originDomainName: 设置回源域名，平台支持通过ip或者域名回源，但二者只能选一，不能同时提供
        @type advOriginConfigs: list of AdvOriginConfig
        @param advOriginConfigs: 复杂回源规则列表
        '''
        self.originIps = originIps
        self.advOriginConfigs = advOriginConfigs


class AdvOriginConfig(object):
    '''复杂回源规则'''
    def __init__(self, carrierCode = "ANY", originSourceEx = None, backToSourceType = "RoundRobin"):
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
        self.backToSourceType = backToSourceType
        self.carrierCode = carrierCode
        self.originSourceEx = originSourceEx

class CacheBehavior(object):
    ''' 缓存行为 '''

    def __init__(self, pathPattern = ".*", ignoreCacheControl = "True", neverCache="False", cacheTtl = "31536000", queryString = "False"):
        '''
        @type priority: int
        @param pathPattern: 设置路径匹配格式，支持*通配符以及|、()等正则字符，举例如下： 所有jpg文件：*.jpg 所有jpg或者gif文件：*.(jpg|gif) a/b/c下所有文件：a/b/c/ a/b/c下的所有jpg或者gif文件：a/b/c/*.(jpg|gif)
        @type ignoreCacheControl: boolean
        @param ignoreCacheControl: 设置是否忽略http头中的cache-control
        @param cacheTtl: 设置缓存时间，单位为s
        '''
        self.pathPattern = pathPattern
        self.neverCache = neverCache
        self.ignoreCacheControl = ignoreCacheControl
        self.cacheTtl = cacheTtl
        self.queryString = queryString

def parseAdvOriginConfigList(nodeList):
    advOriginConfigList = []
    for advOriginConfigNode in nodeList:
        carrierCode = util.getChildNodeText(advOriginConfigNode, 'CarrierCode')
        originSourceEx = util.getChildNodeText(advOriginConfigNode, 'OriginSourceEx')
        advOriginConfig = AdvOriginConfig(carrierCode = carrierCode, originSourceEx = originSourceEx)
        advOriginConfigList.append(advOriginConfig)
    return advOriginConfigList

def parseCacheBehaviorList(nodeList):
    cacheBehaviorList = []
    for cacheBehavior in nodeList:
        pathPattern = util.getChildNodeText(cacheBehavior, 'PathPattern')
        neverCache = util.getChildNodeText(cacheBehavior, 'NeverCache')
        ignoreCacheControl = util.getChildNodeText(cacheBehavior, 'CacheControl')
        if ignoreCacheControl == "Ignore":
            _ignore = "True"
        else:
            _ignore = "False"
        cacheTTL = util.getChildNodeText(cacheBehavior, 'CacheTime')
        forwardedValues = util.getChildNode(cacheBehavior, 'ForwardedValues')
        queryString = util.getChildNodeText(forwardedValues, 'QueryString')
        cacheBehavior = CacheBehavior(pathPattern, _ignore, neverCache, cacheTTL, queryString)
        cacheBehaviorList.append(cacheBehavior)
    return cacheBehaviorList

def parseVisitControlRulesList(nodeList):
    vistControlRulesList = []
    for node in nodeList:
        pathPattern = util.getChildNodeText(node, 'PathPattern')
        whiteList = util.getChildNodeText(node, 'WhiteList')
        blackList = util.getChildNode(node, "BlackList")
        denyIpList = util.getChildNodeList(node, 'DenyIpList')
        visitControlRule = VisitControlRule(pathPattern, whiteList, blackList, denyIpList)
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
    etag = ret.getheader("ETag")
    xmlString = ret.read().decode("utf-8")
    logger.debug("response:" + xmlString)
    print xmlString
    doc = minidom.parseString(xmlString.encode("utf-8"))
    domainNode = util.getChildNode(doc, 'Distribution')
    domainconfig = util.getChildNode(domainNode, 'DistributionConfig')
    if domainconfig != None:
        domainconfig_domains = util.getChildNode(domainconfig, 'Domains')
        domainconfig_domains_domain = util.getChildNode(domainconfig_domains, 'Domain')
        domainName = util.getChildNodeText(domainconfig_domains_domain, 'Aliases')  # sb 帝联把domain_name 藏的很深
        testUrl = util.getChildNodeText(domainconfig_domains_domain, 'TestUrls')
        domainId = util.getChildNodeText(domainNode, 'Id')
        #serviceType = util.getChildNodeText(domainNode, 'service-type') 帝联没有
        faildComment = util.getChildNodeText(domainNode, 'FaildComment')
        comment = util.getChildNodeText(domainconfig, 'Comment')
        #serviceAreas = util.getChildNodeText(domainNode, 'service-areas') 帝联没有
        notUse = util.getChildNodeText(domainconfig, 'NotUse')
        if notUse == 'False':
            enabled = 'True'
        else:
            enabled = 'False'
    else:
        # 查询已删除的域
        domainconfig_domains_domain = domainName = etag = testUrl = comment = faildComment = enabled = None
        domainId = util.getChildNodeText(domainNode, 'Id')
    cname = util.getChildNodeText(domainNode, 'DnionDomain')
    status = util.getChildNodeText(domainNode, 'Status')

    domain = Domain(domainName = domainName,
                    etag = etag,
                    testUrl = testUrl,
                    domainId = domainId,
                    comment = comment,
                    faildComment = faildComment,
                    enabled = enabled,
                    cname = cname,
                    status = status)

    if domainconfig_domains_domain == None:
        originConfigNode = None
    else:
        originConfigNode = util.getChildNode(domainconfig_domains_domain, 'Origin')

    if originConfigNode is not None:
        advOriginConfigListRootNode = util.getChildNode(originConfigNode, 'AdvanceConfig')
        advOriginConfigListNode = util.getChildNode(advOriginConfigListRootNode, 'Item')
        originIps = util.getChildNodeText(advOriginConfigListNode, 'OriginSourceEx')
        #originIps = util.getChildNodeText(originConfigNode, "OriginSource")
        originConfig = OriginConfig(originIps.split(','))
        domain.originConfig = originConfig

    if domainconfig == None:
        cacheBehaviorListRootNode = None
    else:
        cacheBehaviorTop = util.getChildNode(domainconfig, 'CacheBehaviorTop')
        if cacheBehaviorTop is not None:
            cacheBehaviorListRootNode = util.getChildNode(cacheBehaviorTop, 'CacheBehaviors')
        else:
            cacheBehaviorListRootNode = None
    if cacheBehaviorListRootNode is not None:
        cacheBehaviorListNode = util.getChildNodeList(cacheBehaviorListRootNode, 'CacheBehavior')
        if cacheBehaviorListNode is not None:
            cacheBehaviorList = parseCacheBehaviorList(cacheBehaviorListNode)
            domain.cacheBehaviors = cacheBehaviorList

    if domainconfig == None:
        visitControlRulesListRootNode = None
    else:
        visitControlRulesTop = util.getChildNode(domainconfig, 'AclBehaviorsTop')
        visitControlRulesListRootNode = util.getChildNode(visitControlRulesTop, 'AclBehaviors')
    if visitControlRulesListRootNode is not None:
        visitControlRulesListNode = util.getChildNodeList(visitControlRulesListRootNode, 'AclBehavior')
        if visitControlRulesListNode is not None:
            visitControlRulesList = parseVisitControlRulesList(visitControlRulesListNode)
            domain.visitControlRules = visitControlRulesList

    return ProcessResult(0, 'OK', xCncRequestId = requestId, domain = domain, etag=etag);

def domainToXml(domain):
    ''' Domain 对象 转换成 xml '''
    doc = dom.getDOMImplementation().createDocument('', 'Distribution', '')
    domainNode = util.getChildNode(doc, 'Distribution')
    distributionConfig = util.addElement(doc, domainNode, 'DistributionConfig')

    # 写死部分
    customer = util.addElement(doc, domainNode, 'Customer')
    util.addElement(doc, customer, 'Id', '436bd48b')
    platform = util.addElement(doc, domainNode, 'Platform')
    util.addElement(doc, platform, 'Name', 'xnop015')
    util.addElement(doc, platform, 'Type', 'WEB')
    visitControlRulesTop = util.addElement(doc, distributionConfig, 'AclBehaviorsTop')
    defaultAclBehavior = util.addElement(doc, visitControlRulesTop, 'DefaultAclBehavior')
    util.addElement(doc, defaultAclBehavior, 'WhiteList')
    util.addElement(doc, defaultAclBehavior, 'BlackList')
    util.addElement(doc, defaultAclBehavior, 'DenyIpList')
    loggingTree = util.addElement(doc, distributionConfig, 'Logging')
    util.addElement(doc, loggingTree, 'Analytics', 'True')
    util.addElement(doc, loggingTree, 'Format', 'Apache')
    util.addElement(doc, loggingTree, 'SplitTime', '1h')

    domainsTree = util.addElement(doc, distributionConfig, 'Domains')
    domainTree = util.addElement(doc, domainsTree, 'Domain')
    if domain.domainName is not None:
        util.addElement(doc, domainTree, 'Aliases',  domain.domainName)
    if domain.testUrl is not None:
        util.addElement(doc, domainTree, 'TestUrls',  domain.testUrl)
    if domain.comment is not None:
        util.addElement(doc, distributionConfig, 'Comment',  domain.comment)
    if domain.faildComment is not None:
        util.addElement(doc, domainNode, 'FaildComment',  domain.faildComment)
    if domain.enabled is not None:
        if domain.enabled == 'True':
            notUse = 'False'
        else:
            notUse = 'True'
        util.addElement(doc, distributionConfig, 'NotUse',  notUse)
    if domain.cname is not None:
        util.addElement(doc, domainNode, 'DnionDomain',  domain.cname)
    if domain.status is not None:
        util.addElement(doc, domainNode, 'Status', domain.status)
    if domain.domainId is not None:
        util.addElement(doc, domainNode, 'Id', domain.domainId)


    if domain.originConfig is not None:
        originConfigNode = util.addElement(doc, domainTree, 'Origin')
        originIps = domain.originConfig.originIps
        util.addElement(doc, originConfigNode, 'OriginSource', originIps[0])

        # if domain.originConfig.advOriginConfigs is not None:
        advOriginConfigsNode = util.addElement(doc, originConfigNode, 'AdvanceConfig')
        advOriginConfig = AdvOriginConfig()
        # for advOriginConfig in domain.originConfig.advOriginConfigs:
        backToSourceType = advOriginConfig.backToSourceType
        carrierCode = advOriginConfig.carrierCode
        originSourceEx = ','.join(originIps)  # advOriginConfig.originSourceEx
        util.addElement(doc, advOriginConfigsNode, 'BackToSourceType', backToSourceType)
        advOriginConfigNode = util.addElement(doc, advOriginConfigsNode, 'Item')
        util.addElement(doc, advOriginConfigNode, 'CarrierCode', carrierCode)
        util.addElement(doc, advOriginConfigNode, 'OriginSourceEx', originSourceEx)

    if domain.cacheBehaviors is not None:
        cacheBehaviorsTop = util.addElement(doc, distributionConfig, 'CacheBehaviorTop')
        cacheBehaviorsNode = util.addElement(doc, cacheBehaviorsTop, 'CacheBehaviors')
        for cacheBehavior in domain.cacheBehaviors:
            cacheBehaviorNode = util.addElement(doc, cacheBehaviorsNode, 'CacheBehavior')
            util.addElement(doc, cacheBehaviorNode, 'PathPattern', cacheBehavior.pathPattern)
            util.addElement(doc, cacheBehaviorNode, 'NeverCache', cacheBehavior.neverCache)
            if cacheBehavior.ignoreCacheControl == 'True':
                ignore = 'Ignore'
            else:
                ignore = 'NotIgnore'
            util.addElement(doc, cacheBehaviorNode, 'CacheControl', ignore)
            util.addElement(doc, cacheBehaviorNode, 'CacheTime', cacheBehavior.cacheTtl)
            forwardedValues = util.addElement(doc, cacheBehaviorNode, 'ForwardedValues')
            util.addElement(doc, forwardedValues, 'QueryString', cacheBehavior.queryString)

    if domain.visitControlRules is not None:
        visitControlRulesNode = util.addElement(doc, visitControlRulesTop, 'AclBehaviors')
        for visitControl in domain.visitControlRules:
            visitControlNode = util.addElement(doc, visitControlRulesNode, "AclBehavior")
            util.addElement(doc, visitControlNode, 'PathPattern', visitControl.pathPattern)
            util.addElement(doc, visitControlNode, 'WhiteList', visitControl.whiteList)
            util.addElement(doc, visitControlNode, 'BlackList', visitControl.blackList)
            util.addElement(doc, visitControlNode, 'DenyIpList', visitControl.denyIpList)
    return doc.toprettyxml(indent = "", newl="", encoding = 'utf-8')

class ProcessResult(BaseResult):
    '''表示请求的返回结果'''
    def __init__(self, ret, msg, xCncRequestId = None, domain = None, etag = None, domainSummarys = None, location = None,
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
        self.etag = etag
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


######## purgeApi #########
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
    if ret.status == 200:
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

def purgeQueryByPurgeIdXmlToPurgeList(ret_status, ret, purgeId):
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
    purgeItem = PurgeItem(url=path, status=status, rate=rate)
    purgeItems.append(purgeItem)
    purge = Purge(purgeId, requestDate, purgeItems)
    purgeList.append(purge)
    return PurgeQueryResult(ret_status, 'OK', xCncRequestId = requestId, purgeList = purgeList)

def prefetchQueryByPurgeIdXmlToPurgeList(ret_status, ret, purgeId):
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
    itemNodeList = util.getChildNodeList(purgeResultNode, 'Item')
    purgeItems = []
    purgeList = []
    for itemNode in itemNodeList:
        path = util.getChildNodeText(itemNode, "Path")
        status = util.getChildNodeText(itemNode, "Status")
        purgeItem = PurgeItem(url=path, status=status)
        purgeItems.append(purgeItem)
    purge = Purge(purgeId, requestDate, purgeItems)
    purgeList.append(purge)
    return PurgeQueryResult(ret_status, 'OK', xCncRequestId = requestId, purgeList = purgeList)


# 以下为流量
# 为查询流量增加 params
def xmlToFlowPointList(ret, reportType):
    ''' 返回xml 转换成 带 FlowPoint对象列表的FlowProcessResult对象'''
    global X_CNC_REQUEST_ID, X_CNC_LOCATION
    requestId = ret.getheader(X_CNC_REQUEST_ID)

    isoFormat = getDateFormat(reportType)

    xmlString = ret.read().decode("utf-8")
    logging.debug("response:" + xmlString)
    doc = minidom.parseString(xmlString)
    rootNode = util.getChildNode(doc, 'provider')
    dateNode = util.getChildNode(rootNode, 'date')
    flowPointListNode = util.getChildNode(dateNode, 'Product')
    flowPointList = []
    flowDataList = util.getChildNodeList(flowPointListNode, 'flow')
    for flowNode in flowDataList:
        pointStr = flowNode.getAttribute('date')
        # point = datetime.datetime.strptime(pointStr, isoFormat)
        flow = util.getText(flowNode)
        flowPoint = FlowPoint(pointStr, flow)
        flowPointList.append(flowPoint)
    return FlowProcessResult(0, 'OK', xCncRequestId = requestId,
                             flowPoints = flowPointList)

def xmlToBandWidthPointList(ret, reportType):
    ''' 返回xml 转换成 带 FlowPoint对象列表的FlowProcessResult对象'''
    global X_CNC_REQUEST_ID, X_CNC_LOCATION
    requestId = ret.getheader(X_CNC_REQUEST_ID)

    isoFormat = getDateFormat(reportType)

    xmlString = ret.read().decode("utf-8")
    logging.debug("response:" + xmlString)
    doc = minidom.parseString(xmlString)
    rootNode = util.getChildNode(doc, 'provider')
    dateNode = util.getChildNode(rootNode, 'date')
    flowPointListNode = util.getChildNode(dateNode, 'Product')
    flowPointList = []
    flowDataList = util.getChildNodeList(flowPointListNode, 'Traffice')
    for flowNode in flowDataList:
        pointStr = flowNode.getAttribute('time')
        # point = datetime.datetime.strptime(pointStr, isoFormat)
        flow = util.getText(flowNode)
        flowPoint = FlowPoint(pointStr, flow)
        flowPointList.append(flowPoint)
    return FlowProcessResult(0, 'OK', xCncRequestId = requestId,
                             flowPoints = flowPointList)

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