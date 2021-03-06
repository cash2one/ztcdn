__author__ = 'liujiahua'
import logging
# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

#############################################################################
# Identity Service Endpoint
#############################################################################
AUTH_PUBLIC_URI = '192.168.39.170:5000'
ADMIN_TOKEN = '60feb5797e974a89af19e9a40f04ac07'
ADMIN_PROJ = '1234567890'


DL_USER = '123'
DL_PASS = '456'

WS_USER = '123'
WS_PASS = '123'

YY_KEY = '123'

CDN_LOG_DB = 'mysql://root:@localhost/cloud_cdn'
# CDN_LOG_DB = 'mysql://root:root@172.30.250.165/cloud_cdn'


# CNAME DB
#CNAME_DB1_HOST = '172.30.250.186'
#CNAME_DB1_USER = 'dns'
#CNAME_DB1_PASS = 'Kqyygywcw1'
CNAME_DB1_HOST = 'localhost'
CNAME_DB1_USER = 'root'
CNAME_DB1_PASS = ''

#CNAME_DB2_HOST = '172.30.250.149'
#CNAME_DB2_USER = 'cloud_cdn'
#CNAME_DB2_PASS = 'Cloud_Cdn113322'
CNAME_DB2_HOST = 'localhost'
CNAME_DB2_USER = 'root'
CNAME_DB2_PASS = ''

YY_USER = ['dashabi', '2bi', 'cloudcdn_admin']  # addDomain and cname used

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(pathname)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='E:/ztcdn/logs/all.log',
                    filemode='a')


