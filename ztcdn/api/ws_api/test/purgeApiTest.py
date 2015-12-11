# -*- coding: utf-8 -*-
'''
Created on 2013-10-18

@author: zzh
'''
import sys
reload(sys)
#sys.setdefaultencoding('utf8')

import logging
import ztcdn.api.ws_api.api.domainApi as domainApi

logging.basicConfig(level = logging.DEBUG)

api = domainApi.DomainApi()
dateFrom = "2013-09-01 01:00:00"
dateTo = "2013-09-18 12:00:00"

domainId = "193382"
'''
logging.debug("批量清除某域名下缓存")
dirs = ['http://hewenchina.com/static/css/']
urls = ['http://hewenchina.com/static/images/news.jpg', 'http://hewenchina.com/static/images/new222s.jpg' ]
purgeBatch = purgeApi.PurgeBatch(urls, dirs)
result = api.purge(purgeBatch)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId(), result.getLocation()

'''
logging.debug("根据purgeId查缓存")
#purgeId = result.getXCncRequestId()
purgeId = "58cc4f13-5ca1-4ba0-b952-703ca089712e"
result = api.prefetchQueryByPurgeId(purgeId)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId()
for i in result.getPurgeList()[0].itemList:
    print i.status, i.url, i.rate, i.isdir



