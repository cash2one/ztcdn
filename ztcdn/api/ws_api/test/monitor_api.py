__author__ = 'liujiahua'
# -*- coding: utf-8 -*-
import sys
reload(sys)
#sys.setdefaultencoding('utf8')
sys.path.append('/usr/local/ztcdn')
from ztcdn.api.ws_api.api import domainApi
api = domainApi.DomainApi()
result = api.listAll()
if result.getRet() == 0:
    print '0'
else:
    print result.getRet()
#print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId(), result.getLocation()
#print 'domainSummarys:', result.getDomainSummarys()
#for i in result.getDomainSummarys():
#    print i.domainName, i.domainId