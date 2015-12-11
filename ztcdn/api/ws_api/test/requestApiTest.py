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
import ztcdn.api.ws_api.api.requestApi as requestApi

logging.basicConfig(level = logging.DEBUG)

api = requestApi.RequestApi()

logging.debug("对于客户每一次请求记录/任务，都会生成一个 cnc-request-id。客户可以通过该 id查询请求记录，如果是异步的任务(HTTP 响应状态码为 HTTP 202 Accepted 的任务)，也可以通过该接口查询任务最终执行结果。")
requestId = "368cc30b-3ca7-46ee-82b5-07d475b10c6e"
result = api.getRequest(requestId)
print 'result:', result.getRet(), result.getMsg(), result.getXCncRequestId()
print 'requestLog:', result.getRequestLog()
