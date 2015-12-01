#_*_ coding: utf-8 -*-
'''
Created on 2013-10-18

@author: zzh
'''
import sys
reload(sys)
from ztcdn.api.ws_api.api import domainApi
if __name__ == '__main__':
    pass
import logging
import ztcdn.api.ws_api.api.reportApi as reportApi

logging.basicConfig(level = logging.DEBUG)

api = domainApi.DomainApi()



logging.debug("获取全部域名的流量报表")
result = api.getBandWidthReport("jay.ztgame.com","2015-10-01", "2015-11-23")
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId()
print 'flowPoints:'
for i in result.getFlowPoints():
    print i.flow, i.point
"""
logging.debug("获取某域名的流量报表")
result = api.getFlowReport(reportForm, domainId)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId()
print 'flowPoints:', result.getFlowPoints()

logging.debug("获取全部域名的请求数报表")
result = api.getHitReport(reportForm)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId()
print 'hitpoints:', result.getHitPoints()

logging.debug("获取某域名的请求数报表")
result = api.getHitReport(reportForm, domainId)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId()
print 'hitpoints:', result.getHitPoints()

logging.debug("获取某域名的log")
reportForm.reportType = None
result = api.getLog(reportForm, domainId)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId()
print 'logs:', result.getLogs()
"""