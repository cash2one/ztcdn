__author__ = 'liujiahua'
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

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask import abort
from flask import request
from flask import jsonify
from config import AUTH_PUBLIC_URI, ADMIN_TOKEN
import json
import httplib
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/cloud_cdn'
app.config['SQLALCHEMY_BINDS'] = {
    #'cdn_log': 'mysql://root:root@172.30.250.165/cloud_cdn'
    'cdn_log': 'mysql://root:@localhost/cloud_cdn'
}
db = SQLAlchemy(app)

@app.errorhandler(401)
def page_not_found(error):
    return 'Unauthorized', 401


@app.before_request
def before_request():
    token = request.headers.get("X-Auth-Token")
    if request.path == "/cdn_api/tokens":
        pass
    elif not token and request.path != "/cdn_api/tokens":
        abort(401)
    else:
        if validatedToken(token):
            pass
        else:
            return jsonify({"error": "invalid token"}), 400

def validatedToken(token):
    headers = {"X-Auth-Token": "%s" % ADMIN_TOKEN}
    KEYSTONE = AUTH_PUBLIC_URI
    try:
        conn = httplib.HTTPConnection(KEYSTONE)
    except:
        return 'ConnError'
    try:
        if token == ADMIN_TOKEN:
            return True
        conn.request("GET", "/v2.0/tokens/%s" % token, '', headers)
    except:
        return 'ConnError'
    response = conn.getresponse()
    data = response.read()
    dd = json.loads(data)
    if dd.has_key('access'):
        return True
    else:
        return False

from ztcdn import models
#api = Api(app)
#
#class HelloWorld(Resource):
#
#    def get(self):
#        return {'hello': 'world'}
#
#api.add_resource(HelloWorld, '/')
#from unify.api.identity import identity_bp

#app.register_blueprint(identity_bp, url_prefix='/identity')
from ztcdn.api import cdn_api

app.register_blueprint(cdn_api, url_prefix='/cdn_api')
