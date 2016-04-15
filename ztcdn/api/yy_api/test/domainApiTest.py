# -*- coding: utf-8 -*-
'''
Created on 2013-1-10

@author: sinlangxmu@gmail.com
'''
import sys
reload(sys)
#sys.setdefaultencoding('utf8')

if __name__ == '__main__':
    pass
from ztcdn.api.yy_api.api import domainApi
import logging

logging.basicConfig(level = logging.DEBUG)

api = domainApi.DomainApi()

#purgeLocation = "a79af3d0-7188-42bd-a5a9-472355b4dc4e"
#createDomainRequstId = "42b50404-2db3-4802-966c-1b3c9ad42948"
#domainId = "193382"
domainName = "www.hewenchina.com"
domain = domainApi.Domain()
domain.domainName = domainName
domain.serviceType = "web"

originConfig = domainApi.OriginConfig()
originConfig.originIps = ["119.97.171.112"]

domain.originConfig = originConfig

cacheBehavior = domainApi.CacheBehavior()
cacheBehavior.cacheTtl = "315360"
cacheBehavior.pathPattern = "*.jpg"
cacheBehavior.ignoreCacheControl = "True"
domain.cacheBehaviors = [cacheBehavior]


#queryStringSetting = domainApi.QueryStringSetting()
#queryStringSetting.ignoreQueryString = False
#queryStringSetting.pathPattern = ".*"
#domain.queryStringSettings = [queryStringSetting]


#result = api.modify(domain)
#print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId(), result.getLocation()


#result = api.analyticsServer('porn88.ztgame.com', '2016-03-12', '2016-03-12')

#print result.read()

logging.debug("根据purgeId查缓存")
#purgeId = result.getXCncRequestId()
purgeId = "1460018902"
result = api.prefetchQueryByPurgeId(purgeId)
print 'result:', result.getRet(), result.getMsg()
for i in result.getPurgeList()[0].itemList:
    print i.status, i.url, i.rate


"""
logging.debug("获取指定频道信息")
result = api.find('d8e2141e-e5e3-11e5-8ad5-e03f4978b2ff')
print 'result:', result.domain.cname,  result.domain.status, result.getRet(), result.getMsg(), result.getXCncRequestId()
for i in result.domain.cacheBehaviors:
    print i.pathPattern, i.ignoreCacheControl, i.cacheTtl



result = api.delete('')
print 'result:', result.getRet(), result.getMsg()


logging.debug("预热文件")
#dirs = ['http://hewenchina.com/static/css/']
urls = ['http://www.hewenchina.com/static/images/news.jpg', 'http://www.hewenchina.com/static/images/new222s.jpg' ]
purgeBatch = domainApi.PurgeBatch(urls=urls)
result = api.prefetch(purgeBatch)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId()


logging.debug("获取用户下的频道列表")
result = api.listAll()
print 'result:', result.getRet(), result.getMsg()
print 'domainSummarys:', result.domainSummarys
for i in result.domainSummarys:
    print i["name"], i["id"]

logging.debug("获取带宽")
result = api.getBandWidthReport('www.hewenchina.com', '2016-03-05', '2016-03-08')
print 'result:', result.getRet(), result.getMsg()
print 'flowPoints:'
for i in result.getFlowPoints():
    print i.flow, i.point



logging.debug("获取流量")
result = api.getFlowReport('www.hewenchina.com', '2016-03-05', '2016-03-08')
print 'result:', result.getRet(), result.getMsg()
print 'flowPoints:'
for i in result.getFlowPoints():
    print type(i.flow), i.point




logging.debug("根据purgeId查缓存")
#purgeId = result.getXCncRequestId()
purgeId = "1457320262"
result = api.purgeQueryByPurgeId(purgeId)
print 'result:', result.getRet(), result.getMsg()
for i in result.getPurgeList()[0].itemList:
    print i.status, i.url, i.rate




logging.debug("批量清除某域名下缓存")
#dirs = ['http://hewenchina.com/static/css/']
urls = ['http://www.hewenchina.com/static/images/news.jpg', 'http://www.hewenchina.com/static/images/new222s.jpg' ]
purgeBatch = domainApi.PurgeBatch(urls=urls)
result = api.purge(purgeBatch)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId()
# batch = 1457320262



result = api.modify(domain)
print 'result:', result.getRet(), result.getMsg()


logging.debug("获取用户下的频道列表")
result = api.listAll()
print 'result:', result.getRet(), result.getMsg()
print 'domainSummarys:', result.domainSummarys
for i in result.domainSummarys:
    print i["name"], i["id"]

result = api.add(domain)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId()

result = api.find("1283933")
print 'result:', result.domain.cname,  result.domain.status, result.getRet(), result.getMsg(), result.getXCncRequestId()
print 'domain:', domainApi.domainToXml(result.domain)
"""
'''
logging.debug("获取指定频道信息")
result = api.find('1262421')
print 'result:', result.domain.cname,  result.domain.status, result.getRet(), result.getMsg(), result.getXCncRequestId()
print 'domain:', domainApi.domainToXml(result.domain)





advOriginConfigMult = domainApi.AdvOriginConfig()
advOriginConfigMult.isps = ["dx", "jyw"]
advOriginConfigMult.backupIps = ["192.168.0.1",]
advOriginConfigMult.masterIps = ["115.29.209.110",]
advOriginConfigMult.detectUrl = detectUrl
advOriginConfigMult.detectPeriod = 10

advOriginConfig = domainApi.AdvOriginConfig()
advOriginConfig.isps = ["wt"]
advOriginConfig.backupIps = ["192.168.0.1",]
advOriginConfig.masterIps = ["115.29.209.110",]
advOriginConfig.detectUrl = detectUrl
advOriginConfig.detectPeriod = 10

queryStringSetting = domainApi.QueryStringSetting()
queryStringSetting.ignoreQueryString = False
queryStringSetting.pathPattern = ".*"
domain.queryStringSettings = [queryStringSetting]

originConfig.advOriginConfigs = [advOriginConfigMult, advOriginConfig]
domain.originConfig = originConfig

cacheBehavior = domainApi.CacheBehavior()
cacheBehavior.priority = 1
cacheBehavior.cacheTtl = 10
cacheBehavior.pathPattern = "/(a|b)/*.html"
cacheBehavior.ignoreCacheControl = False
domain.cacheBehaviors = [cacheBehavior]


1. path-pattern必填
2. valid-referers、invalid-referers和forbidden-ips至少填写其中一个。
3. valid-referers和invalid-referers不得同时提交。
4. allowNullReferer只在validReferers不为空的时候有效

visitControlRule = domainApi.VisitControlRule()
visitControlRule.forbiddenIps = ["192.168.1.8", "192.168.1.7"]
visitControlRule.allowNullReferer = True
#visitControlRule.invalidReferers = ["www.a.com"]
visitControlRule.validReferers = ["www.b.com"]
visitControlRule.pathPattern = "/(a|b)/*.html"
domain.visitControlRules = [visitControlRule]


logging.debug("添加频道")
result = api.add(domain)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId(), result.getLocation()
print result.cname







logging.debug("获取指定频道信息")
result = api.find('1251422')
print 'result:', result.domain.cname,  result.domain.status, result.getRet(), result.getMsg(), result.getXCncRequestId()
print 'domain:', domainApi.domainToXml(result.domain)





logging.debug("修改指定频道")
oriDomain = result.getDomain()
oriDomain.domainId = domainId
oriDomain.comment = "xxxxx_modify"
result = api.modify(oriDomain)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId(), result.getLocation()

logging.debug("启用指定频道")
result = api.enable(domainId)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId()

logging.debug("禁用指定频道")
result = api.disable(domainId)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId()

logging.debug("删除指定频道")
result = api.delete("1250897")
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId(), result.getLocation()
'''
