# -*- coding: utf-8 -*-
__author__ = 'liujiahua'
class Domain(object):
    '''表示为域名对象'''
    def __init__(self, domainName = None, serviceType = 'web', etag = None, testUrl = None, queryStringSettings = None,
                 domainId = None, comment = "create", faildComment = None, serviceAreas = None, status = None, enabled = "False", cname = None,
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
    def __init__(self, pathPattern = None, allowNullReferer = None, validReferers = None, invalidReferers = None, forbiddenIps = None,
                 whiteList = None, blackList = None, denyIpList = None):
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
        self.whiteList = whiteList
        self.blackList = blackList
        self.denyIpList = denyIpList

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
    def __init__(self, isps = '', masterIps = '', backupIps = '', detectUrl = '', detectPeriod = '',
                 carrierCode = "ANY", originSourceEx = None, backToSourceType = "RoundRobin"):
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
        self.carrierCode = carrierCode
        self.originSourceEx = originSourceEx
        self.backToSourceType = backToSourceType

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
        self.ignoreCacheControl = ignoreCacheControl
        self.neverCache = neverCache
        self.cacheTtl = cacheTtl
        self.queryString = queryString

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

class User(object):
    def __init__(self, token=None, username=None, proj_list=None):
        self.token = token
        self.username = username
        self.proj_list = proj_list