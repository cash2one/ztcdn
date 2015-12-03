__author__ = 'liujiahua'
from flask import jsonify
from flask import request
from ztcdn.util.apiUtil import getTokenFromKS
from ztcdn.api import cdn_api

@cdn_api.route('/tokens', methods=['POST'])
def tokens():
    username = request.json.get("username")
    password = request.json.get("password")
    token = getTokenFromKS(username, password)
    return jsonify(token)