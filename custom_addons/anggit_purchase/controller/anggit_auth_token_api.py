from odoo import http, fields
from odoo.http import request, Response
import json
import secrets
from datetime import datetime, timedelta

class AnggitAuthTokenApi(http.Controller):
    @http.route('/api/login', type='http', auth='none', methods=['POST'], csrf=False)
    def login(self, **kwargs):
        try:
            body = json.loads(request.httprequest.data)
        except Exception:
            return Response(
                json.dumps({'ok': False, 'error': 'Invalid JSON format.'}),
                status=400,
                headers=[('Content-Type', 'application/json')]
            )

        username = body.get('username')
        password = body.get('password')

        if not username or not password:
            return Response(
                json.dumps({'ok': False, 'error': 'Username dan password wajib diisi.'}),
                status=400,
                headers=[('Content-Type', 'application/json')]
            )

        try:
            uid = request.session.authenticate(request.db, username, password)
            if uid:
                user = request.env['res.users'].sudo().browse(uid)
                if user.login != 'admin':
                    return Response(
                        json.dumps({'ok': False, 'error': 'Akses ditolak. Hanya admin yang diizinkan.'}),
                        status=403,
                        headers=[('Content-Type', 'application/json')]
                    )

                # Generate token
                token_str = secrets.token_urlsafe(32)
                expires = fields.Datetime.now() + timedelta(hours=24)

                # Simpan token
                request.env['api.token'].sudo().create({
                    'user_id': uid,
                    'token': token_str,
                    'expires_at': expires
                })

                return Response(
                    json.dumps({'ok': True, 'token': token_str}),
                    headers=[('Content-Type', 'application/json')]
                )
            else:
                return Response(
                    json.dumps({'ok': False, 'error': 'Login gagal.'}),
                    status=401,
                    headers=[('Content-Type', 'application/json')]
                )
        except Exception as e:
            return Response(
                json.dumps({'ok': False, 'error': str(e)}),
                status=500,
                headers=[('Content-Type', 'application/json')]
            )