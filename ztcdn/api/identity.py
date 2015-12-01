__author__ = 'liujiahua'
from flask import Blueprint
from flask import jsonify
from flask import request

import requests
from urlparse import urljoin
from ztcdn.util.apiUtil import getTokenFromKS
from ztcdn.api import cdn_api
from flask import abort

@cdn_api.route('/tokens', methods=['POST'])
def tokens():
    username = request.json.get("username")
    password = request.json.get("password")
    token = getTokenFromKS(username, password)
    return jsonify(token)


'''
@cdn_api.route('/projects/<user_id>', methods=['GET'])
def tenants(user_id):
    url = PROJECTS_URI % user_id
    kwargs = {'headers': {}, 'data': request.get_data()}
    kwargs['headers']['X-Auth-Token'] = request.headers.get('7')
    resp = requests.Session().request(request.method, url, **kwargs)
    return resp.content


@cdn_api.route('/users', methods=['GET', 'POST'])
def user_list():
    url = urljoin(AUTH_ADMIN_URI, request.path)
    kwargs = {'headers': {}}
    kwargs['data'] = request.data
    kwargs['headers']['X-Auth-Token'] = request.headers.get('X-Auth-Token')
    kwargs['headers']['Content-Type'] = 'application/json'
    print 'method', request.method
    print 'url', url
    print kwargs
    resp = requests.Session().request(request.method, url, **kwargs)

    return resp.text
'''