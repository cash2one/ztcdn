# -*- coding: utf-8 -*-
__author__ = 'liujiahua'

from ztcdn.api.dl_api.api import domainApi
import logging

api = domainApi.DomainApi()

domain = domainApi.Domain()
domainName = "hewenchina.com"
detectUrl = "http://hewenchina.com"
domain.domainName = domainName
domain.testUrl = "http://hewenchina.com/static/images/services.jpg"
originConfig = domainApi.OriginConfig()
originConfig.originIps = ["115.29.209.110",]

advOriginConfigMult = domainApi.AdvOriginConfig()
originConfig.advOriginConfigs = [advOriginConfigMult,]
domain.originConfig = originConfig

cacheBehavior = domainApi.CacheBehavior()
domain.cacheBehaviors = [cacheBehavior]

result = api.delete('')
print 'result:', result.getRet(), result.getMsg()

'''

logging.debug("获取用户下的频道列表")
result = api.listAll()
print 'result:', result


logging.debug("添加频道")
result = api.add(domain)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId(), result.getLocation()
print result.cname, result.domain.status




logging.debug("获取指定频道信息")
result = api.find('eb82d34cd22e4cd7a4d826268378722e')
print 'result:', result.domain.cname, result.domain.status, result.getRet(), result.getMsg(), result.getXCncRequestId()
print 'domaimXML', result.domain.comment
print 'domain:', domainApi.domainToXml(result.getDomain())

'''