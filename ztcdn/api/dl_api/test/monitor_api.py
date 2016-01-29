__author__ = 'liujiahua'
import sys
sys.path.append('/usr/local/ztcdn')
from ztcdn.api.dl_api.api import domainApi

api = domainApi.DomainApi()
result = api.listAll()
if type(result) == str:
    print '0'
else:
    print result.getRet()