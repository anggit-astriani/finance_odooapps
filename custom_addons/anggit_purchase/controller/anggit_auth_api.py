# auth_api.py
from odoo import http 
from odoo.http import request, Response 
import json 
 
class AnggitAuthApi(http.Controller): 
    @http.route('/api/login', type='json', auth='none', methods=['POST'], csrf=False) 
    def login(self, **params): 
        try: 
            body = json.loads(request.httprequest.data) 
        except Exception: 
            return {'ok': False, 'error': 'Invalid JSON format.'} 
 
        username = body.get('username') 
        password = body.get('password') 
 
        if not username or not password: 
            return {'ok': False, 'error': 'Username dan password wajib diisi.'} 
 
        try: 
            uid = request.session.authenticate(request.db, username, password) 
            if uid: 
                user = request.env['res.users'].sudo().browse(uid) 
                return { 
                    'ok': True, 
                    'session_id': request.session.sid, 
                    'username': user.login, 
                    'uid': uid,
                    'is_admin': user.login == 'admin'  # Info tambahan untuk client
                } 
            else: 
                return {'ok': False, 'error': 'Login gagal. Username atau password salah.'} 
        except Exception as e: 
            return {'ok': False, 'error': str(e)}