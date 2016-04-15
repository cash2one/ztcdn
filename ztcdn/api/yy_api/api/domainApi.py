from __future__ import division
# -*- coding: utf-8 -*-

from ztcdn.config import YY_KEY
from ztcdn.config import logging
import ztcdn.api.yy_api.util.ApiUtil as util
from ztcdn.api.yy_api.util.ApiUtil import BaseResult, getDomainNameById, getDomainNameByPurgeId
import datetime
import re
import sys
import json
import traceback
import urllib
import uuid

logger = logging.getLogger(__name__)


class DomainApi(object):
    ''' 域名操作API '''
    HOST = 'http://openapi.exclouds.com'
    #HOST = 'http://192.168.27.161:8080/cloudcdn'
    #HOST = 'http://localhost:8080/cloud-cdn'
    ''' api服务地址 '''

    def __init__(self):
        self.headers = {'Authorization': YY_KEY,
                        'Date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Host': 'openapi.exclouds.com'}
    
    def add(self, domain):
        ''' 创建加速域名 
        @param domain:  新增加速域名构建的Domain对象实例
        @rtype: ProcessResult对象
        @return: 通过ProcessResult.getLocation()新域名的url
        '''
        url = self.HOST + "/configService/addDomain"
        try:
            header = self.headers.copy()
            header["Content-Type"] = 'application/x-www-form-urlencoded'
            post = domainToJson(domain)
            params = urllib.urlencode({"domain": post.encode('utf8')})
            logger.debug('Add request: %s' % post)
            url = self.HOST + "/configService/addDomain?%s" % params
            ret = util.httpReqeust(url, '', header, "POST")
            if ret.status == 200:
                url2 = self.HOST + "/configService/domainDetail?domain=" + domain.domainName
                post2 = ''
                ret2 = util.httpReqeust(url2, post2, self.headers, "GET")
                return res_fmt(ret2)
            else:
                return res_fmt(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))


    def listAll(self):
        ''' 获取加速所有域名列表'''
        url = self.HOST + "/configService/domainList"
        try:
            post = ''
            ret = util.httpReqeust(url, post, self.headers, "GET")
            return res_fmt(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))

    
    def find(self, domainId):
        ''' 获取加速域名配置  
        @type domainId: str
        @param domainId : 指定查找的域名ID
        @rtype: ProcessResult对象
        @return: 通过ProcessResult.getDomain()返回指定的域名信息的Domain实例
        '''
        domain_name = getDomainNameById(domainId)
        url = self.HOST + "/configService/domainDetail?domain=" + domain_name
        try:
            post = ''
            logger.debug('Find request: %s' % url)
            ret = util.httpReqeust(url, post, self.headers, "GET")
            return res_fmt(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))


    def modify(self, domain):
        ''' 修改加速域名配置 
        @type domain: Domain
        @param domain : 构建需要修改的域名的Domain实例, domain中必须设置domanId字段
        @rtype: ProcessResult对象
        @return: 返回ProcessResult对象
        '''
        header = self.headers.copy()
        header["Content-Type"] = 'application/x-www-form-urlencoded'
        post = domainToJson4Update(domain)
        params = urllib.urlencode(post)
        logger.debug('Modify request: %s' % post)
        url = self.HOST + "/configService/upDomain?%s" % params
        try:
            ret = util.httpReqeust(url, '', header, "POST")
            return res_fmt(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))

    
    def delete(self, domainId):
        ''' 删除加速域名 
        @param domainId : 指定待删除的域名ID
        @rtype: ProcessResult对象
        @return: 返回ProcessResult对象
        '''
        header = self.headers.copy()
        header["Content-Type"] = 'application/x-www-form-urlencoded'
        try:
            domain_name = getDomainNameById(domainId)
            post = {
                "domain": domain_name,
                "config": '{"op": "OFF"}'
            }
            params = urllib.urlencode(post)
            logger.debug('Delete request: %s' % post)
            url = self.HOST + "/configService/upDomain?%s" % params
            ret = util.httpReqeust(url, '', header, "POST")
            return res_fmt(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))

    
    def disable(self, domainId):
        pass
    
    def enable(self, domainId):
        pass

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
        header = self.headers.copy()
        header["Content-Type"] = 'application/x-www-form-urlencoded'
        if purgeBatch.urls is not None:
            url_list = purgeBatch.urls
        if purgeBatch.dirs is not None:
            url_list = purgeBatch.dirs
        url_str = ','.join(url_list)
        try:
            post = {"url": '%s' % url_str}
            logger.debug('Purge request: %s' % url_str)
            params = urllib.urlencode(post)
            url = self.HOST + '/contentService/AddRefresh?%s' % params
            ret = util.httpReqeust(url, '', header, "POST")
            return res_fmt(ret)
        except Exception, e:
            traceback.print_exc(file = sys.stdout)
            return ProcessResult(-1, str(e))


    def purgeQueryByPurgeId(self, purgeId):
        ''' 根据purgeId 查询 缓存记录
        @param purgeId: 缓存id
        @rtype: PurgeQueryResult
        @return: 返回PurgeQueryResult结果,可以 通过PurgeQueryResult.getPurgeList()获取purge记录条目的列表
        '''
        url = self.HOST + "/contentService/QueryBatchRefresh?batch=%s" % str(purgeId)
        try:
            logger.debug('purgeQueryByPurgeId request: %s' % url)
            ret = util.httpReqeust(url, "", self.headers, "GET")
            return res_fmt(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))


    def prefetch(self, purgeBatch):
        header = self.headers.copy()
        header['Host'] = 'service.exclouds.com'
        url_list = purgeBatch.urls
        url_str = ','.join(url_list)
        try:
            post = {"url": '%s' % url_str}
            logger.debug('Prefetch request: %s' % url_str)
            params = urllib.urlencode(post)
            url = self.HOST + '/publishService/AddDelivery?%s' % params
            ret = util.httpReqeust(url, '', header, "POST")
            return res_fmt(ret)
        except Exception, e:
            traceback.print_exc(file = sys.stdout)
            return ProcessResult(-1, str(e))

    def prefetchQueryByPurgeId(self, purgeId):
        header = self.headers.copy()
        header['Host'] = 'service.exclouds.com'

        try:
            post = {"batch": '%s' % purgeId, "type": "json"}
            logger.debug('prefetchQueryByPurgeId request: %s' % post)
            params = urllib.urlencode(post)
            url = self.HOST + '/publishService/QueryBatchDelivery?%s' % params
            ret = util.httpReqeust(url, '', header, "POST")
            return prefetch_res_fmt(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))


    def getFlowReport(self, domainName, start, end):
        ''' 获取某域名流量报表 如果domainId 为None,表示 查汇总信息
        @type reportForm: ReportForm
        @param reportForm:  请求的起止时间和报表粒度
        @rtype: FlowRrocessResult
        @return: 通过FlowProcessResult.getFlowPoints() 获得流量查询结果
        '''

        try:
            post = {
                "domain": domainName,
                "beginDate": start,
                "endDate": end
            }
            params = urllib.urlencode(post)
            logger.debug('getFlowReport request: %s' % post)
            url = self.HOST + "/dataService/QueryDailyFlow?%s" % params
            ret = util.httpReqeust(url, '', self.headers, "GET")
            return report_res_fmt(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))


    def getBandWidthReport(self, domainName, start, end):
        ''' 获取某域名带宽报表 如果domainId 为None,表示 查汇总信息
        @type reportForm: ReportForm
        @param reportForm:  请求的起止时间和报表粒度
        @rtype: FlowRrocessResult
        @return: 通过FlowProcessResult.getFlowPoints() 获得流量查询结果
        '''
        try:
            post = {
                "domain": domainName,
                "beginDate": start,
                "endDate": end
            }
            params = urllib.urlencode(post)
            logger.debug('getFlowReport request: %s' % post)
            url = self.HOST + "/dataService/QueryBandwidth?%s" % params
            ret = util.httpReqeust(url, '', self.headers, "GET")
            return report_res_fmt(ret)
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))


    def analyticsServer(self, domain_name, start, end):
        try:
            post = {
                "domain": domain_name,
                "beginDate": start,
                "endDate": end
            }
            params = urllib.urlencode(post)
            logger.debug('getFlowReport request: %s' % post)
            url = self.HOST + "/dataService/QueryTopURL?%s" % params
            ret = util.httpReqeust(url, '', self.headers, "GET")
            return ret
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            return ProcessResult(-1, str(e))
    """
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
    """

class Domain(object):
    '''表示为域名对象'''
    def __init__(self, domainName = None, serviceType = None, etag = None,
                 domainId = None, serviceAreas = None,
                 status = None, enabled = "True", cname = None,
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
        self.serviceType = serviceType
        self.domainId = domainId
        self.etag = etag
        self.serviceAreas = serviceAreas
        self.status = status
        self.enabled = enabled
        self.cname = cname
        self.originConfig = originConfig
        self.cacheBehaviors = cacheBehaviors
        self.visitControlRules = visitControlRules


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


class CacheBehavior(object):
    ''' 缓存行为 '''

    def __init__(self, pathPattern = ".*", ignoreCacheControl = "True", cacheTtl = "31536000"):
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


class ProcessResult(BaseResult):
    '''表示请求的返回结果'''
    def __init__(self, ret, msg, xCncRequestId = None, domain = None, etag = None, domainSummarys = None, location = None,
                 cname = None, purgeList = None, flowPoints=None):
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
        self.purgeList = purgeList
        self.flowPoints = flowPoints

    def getPurgeList(self):
        '''通过getPurgeList方法获得返回结果中的purge记录条目列表'''
        return self.purgeList

    def getFlowPoints(self):
        return self.flowPoints


# 流量单个点类
class FlowPoint(object):
    '''流量统计结果'''
    def __init__(self, point=None, flow=None):
        '''初始化
        @param point: 流量统计时间点
        @param flow: 流量统计值,单位为M
        '''
        self.point = point
        self.flow = flow

def res_fmt(ret):
    # 返回结果格式化
    data = ret.read()
    logger.debug('response: %s' % data)
    dd = json.loads(data)
    if dd.has_key("code"):
        if dd["code"] == 200:
            code = 0
        else:
            code = dd["code"]
    else:
        code = 0  # 查询缓存进度没有这个 code

    msg = dd["message"] if dd.has_key("message") else ''
    domain_list = dd["domains"] if dd.has_key('domains') else None
    domain = jsonToDomain(dd["domain"]) if dd.has_key('domain') else None
    batch = dd["batch"] if dd.has_key("batch") else None

    # 查询缓存结果, 只返回一条
    purge_list = []
    if dd.has_key("results"):
        path_list = []
        purge_items1 = []
        rate_total = 0
        status = 'success'
        for i in dd["results"]:
            path_list.append(i["url"])
            _rate = int(float(i["precent"].replace('%', '')))
            if _rate != 100:
                status = 'wait'
            rate_total += _rate
        rate = round(rate_total/len(dd["results"]), 2)
        path = ','.join(path_list)
        purge_item1 = PurgeItem(path, status, str(rate))
        purge_items1.append(purge_item1)
        purge = Purge(itemList=purge_items1)
        purge_list.append(purge)
    return ProcessResult(code, msg, xCncRequestId=batch, domain=domain, domainSummarys=domain_list, purgeList=purge_list)

# 专门为处理查询预缓存结果的方法
def prefetch_res_fmt(ret):
    dd = json.loads(ret.read())
    logger.debug('prefetchQueryByPurgeId response: %s' % dd)
    if dd.has_key("code"):
        if dd["code"] == 200:
            code = 0
        else:
            code = dd["code"]
    else:
        code = 0  # 查询缓存进度没有这个 code
    msg = dd["message"] if dd.has_key("message") else ''
    # 查询缓存结果, 返回多条， for j in result.getPurgeList()[0].itemList:
    purge_list = []
    if dd.has_key("results"):
        purge_items1 = []
        for i in dd["results"]:
            _rate = 0
            if i["status"] == 'sync finish':
                status = 'success'
            elif re.match('error', i["status"]):
                status = 'failure'
            elif i["status"] == 'sync failed':
                status = 'failure'
            elif i["status"] == 'download failed':
                status = 'failure'
            else:
                status = 'run'
            purge_item1 = PurgeItem(i['url'], status, str(_rate))
            purge_items1.append(purge_item1)
        purge = Purge(itemList=purge_items1)
        purge_list.append(purge)
    return ProcessResult(code, msg, purgeList=purge_list)

# 专门为处理流量和带宽查询返回结果的方法
def report_res_fmt(ret):
    dd = json.loads(ret.read())
    logger.debug('getFlowReport response: %s' % dd)
    flowPoints = []
    if dd.has_key("results"):
        for i in dd["results"]:
            if i.has_key('date'):
                # 是查询流量
                # 20160307 --> 2016-03-07
                point = i["date"][:4] + '-' + i["date"][4:6] + '-' + i["date"][6:8]
                # GB 转 MB
                flow = i["traffic"] * 1000
                flowPoint = FlowPoint(point, flow)
                flowPoints.append(flowPoint)
            if i.has_key('time'):
                # 是带宽查询
                timeStamp = i['time']
                dateArray = datetime.datetime.fromtimestamp(timeStamp)
                point = dateArray.strftime("%Y-%m-%d %H:%M")
                flow = i["traffic"]  # 逸云已经是 Mbps
                flowPoint = FlowPoint(point, flow)
                flowPoints.append(flowPoint)

    if dd.has_key("code"):
        if dd["code"] == 200:
            code = 0
        else:
            code = dd["code"]
    else:
        code = 0  # 查询缓存进度没有这个 code
    msg = dd["message"] if dd.has_key("message") else ''

    return ProcessResult(code, msg, flowPoints=flowPoints)

# 传入的 domain 对象转换成逸云的 json 格式
def domainToJson(domain):
    domain_type = domain.serviceType
    domain_type = 'FTP' if domain_type == 'download' else 'WEB'
    json_str = {
        "name": domain.domainName,
        "source": domain.originConfig.originIps,
        "cachearea": ["CN"],
        "type": domain_type,
        "status": "FORMAL",
        "host": domain.domainName
    }
    if domain.cacheBehaviors:
        cacheBehaviors = []
        for i in domain.cacheBehaviors:
            item = {
                "path-pattern": i.pathPattern,
                "cache-ttl": i.cacheTtl,
                "ignore-cache-control": i.ignoreCacheControl.lower()
            }
            cacheBehaviors.append(item)
        json_str["cache-behaviors"] = cacheBehaviors
    return json.dumps(json_str)

# 将传入的 domain 对象转换成逸云的 json 格式， 为更新域名所用
def domainToJson4Update(domain):
    config = {
        "op": "UP",
        "source": domain.originConfig.originIps,
    }
    if domain.cacheBehaviors:
        cacheBehaviors = []
        for i in domain.cacheBehaviors:
            item = {
                "path-pattern": i.pathPattern,
                "cache-ttl": i.cacheTtl,
                "ignore-cache-control": i.ignoreCacheControl.lower()
            }
            cacheBehaviors.append(item)
        config["cache-behaviors"] = cacheBehaviors

    post = {
        "domain": domain.domainName,
        "config": json.dumps(config).encode('utf-8')
    }
    return post

# 将返回的域名 json 格式转换成 domain 对象
def jsonToDomain(json_dict):
    random_id = uuid.uuid1()
    domain_id = json_dict.get('id', '')
    if not domain_id:
        domain_id = random_id
    domain_name = json_dict.get('name', '')
    domain_cname = json_dict.get('alias', '')
    if not domain_cname:
        domain_cname = domain_name + '.scsdns.com'
    # source ip
    ip_set = json.loads(json_dict.get('source', ''))
    originConfig = OriginConfig(ip_set)
    domain_type = json_dict.get('type', '').lower()
    domain_status = json_dict.get('status', '')  # 需不需要处理
    if domain_status == 'FORMAL':
        domain_status = 'Deployed'
    else:
        domain_status = 'InProgress'

    domain = Domain(domainName=domain_name,
                    domainId=domain_id,
                    cname=domain_cname,
                    serviceType=domain_type,
                    status=domain_status,
                    originConfig=originConfig
                    )

    if json_dict.has_key('cacheBehaviors'):
        cacheBehaviors = []
        caches = json.loads(json_dict['cacheBehaviors'])
        for c in caches:
            cacheBehaviors.append(CacheBehavior(c["path-pattern"],
                                                c["ignore-cache-control"].capitalize(),  # 首字母大写
                                                c["cache-ttl"]))
        domain.cacheBehaviors = cacheBehaviors
    return domain


# 刷新缓存入口类
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

# 缓存查询返回单个类
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





