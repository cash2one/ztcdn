# -*- coding: utf-8 -*-
'''
Created on 2013-10-18

@author: zzh
'''
import sys
reload(sys)
#sys.setdefaultencoding('utf8')

import logging
import ztcdn.api.ws_api.api.purgeApi as purgeApi

logging.basicConfig(level = logging.DEBUG)

api = purgeApi.PurgeApi("giant_cdn", "8f8394b91653afa3")
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
purgeId = "d6479a88-55de-4f2f-9851-3f9d98e5c108"
result = api.purgeQueryByPurgeId(purgeId)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId()
for i in result.getPurgeList()[0].itemList:
    print i.status, i.url, i.rate, i.isdir



