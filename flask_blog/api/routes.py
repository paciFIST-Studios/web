from flask import Blueprint, render_template, request

api = Blueprint('api', __name__)


version = '0.1'
api_version = f'/api/{version}'
api_users = f'/api/{version}/users'
api_tokens = f'/api/{version}/tokens'

# api -------------------------------------------------------------------------
@api.route('/api')
def restful_api_version():
    return {'version': version}

@api.route(api_version)
def restful_api():
    return {'response': 200}

# users -----------------------------------------------------------------------
@api.route(api_users, methods=['POST'])
def users_post():
    return {'users': 'POST'}

@api.route(api_users, methods=['GET'])
def users_get():
    return {'users': 'GET'}

@api.route(api_users, methods=['PUT'])
def users_put():
    return {'users': 'PUT'}

@api.route(api_users, methods=['DELETE'])
def users_delete():
    return {'users': 'DELETE'}

# tokens ----------------------------------------------------------------------
@api.route(api_tokens, methods=['POST'])
def tokens_post():
    return {'tokens': 'POST'}

@api.route(api_tokens, methods=['GET'])
def tokens_get():
    return {'tokens': 'GET'}

@api.route(api_tokens, methods=['PUT'])
def tokens_put():
    return {'tokens': 'PUT'}

@api.route(api_tokens, methods=['DELETE'])
def tokens_delete():
    return {'tokens': 'DELETE'}
