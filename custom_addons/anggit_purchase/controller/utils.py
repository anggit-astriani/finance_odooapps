from odoo.http import Response
import json
from datetime import datetime
from odoo.http import request
from odoo import fields

def validate_bearer_token(authorization):
        auth_header = authorization
        print('utils1')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response(
                json.dumps({'ok': False, 'error': 'Missing or invalid Authorization header.'}),
                status=401,
                headers=[('Content-Type', 'application/json')]
            )

        token = auth_header.split(' ')[1]
        print('utils2')
        token_record = request.env['api.token'].sudo().search([('token', '=', token)], limit=1)
        print('utils3')
        if not token_record or token_record.expires_at < fields.Datetime.now():
            return Response(
                json.dumps({'ok': False, 'error': 'Token invalid atau expired.'}),
                status=401,
                headers=[('Content-Type', 'application/json')]
            )

        # Set user context
        print('utils4')
        # request.uid = token_record.user_id.id
        print(token_record[0].user_id)
        return token_record[0].user_id
        # return None

# def validate_bearer_token(func):
#     def wrapper(self, authorization):
        
#         auth_header = authorization
#         if not auth_header or not auth_header.startswith('Bearer '):
#             return Response(
#                 json.dumps({'ok': False, 'error': 'Missing or invalid Authorization header.'}),
#                 status=401,
#                 headers=[('Content-Type', 'application/json')]
#             )

#         token = auth_header.split(' ')[1]
#         token_record = request.env['api.token'].sudo().search([('token', '=', token)], limit=1)
#         if not token_record or token_record.expires_at < fields.Datetime.now():
#             return Response(
#                 json.dumps({'ok': False, 'error': 'Token invalid atau expired.'}),
#                 status=401,
#                 headers=[('Content-Type', 'application/json')]
#             )

#         # Set user context
#         request.uid = token_record.user_id.id
#         return func(self, authorization)

#     return wrapper