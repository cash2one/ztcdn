#_*_ coding: utf-8 -*-
'''
Created on 2013-10-18

@author: zzh
'''
import sys 
reload(sys) 
#sys.setdefaultencoding('utf8')

if __name__ == '__main__':
    pass
import logging
import ztcdn.api.ws_api.api.domainApi as domainApi


api = domainApi.DomainApi()

requestId = "5b9d282e-d2d5-4044-af34-d37667300fed"
result = api.getReqStatus(requestId)
print 'result:', result
