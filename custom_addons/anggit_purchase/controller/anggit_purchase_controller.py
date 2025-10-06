from odoo import http
from odoo.http import request, Response
import json
from .utils import validate_bearer_token

class AnggitPurchaseRestApi(http.Controller):

    # def _check_admin(self): 
    #     """Check if current user is admin"""
    #     user = request.env.user 
    #     if user.login != 'admin': 
    #         return Response( 
    #             json.dumps({'ok': False, 'error': 'Akses ditolak. Hanya admin yang diizinkan.'}), 
    #             status=403, 
    #             headers=[('Content-Type', 'application/json')] 
    #         ) 
    #     return None 

    @http.route('/api/anggit_purchase', type='http', auth='user', methods=['GET'], csrf=False)
    def get_anggit_purchase(self, **params):
        # auth_error = self._check_admin() 
        # if auth_error: 
        #     return auth_error 

        limit = int(params.get('limit', 10))
        status = params.get('status')

        domain = []
        if status:
            domain.append(('status', '=', status))
        anggit_purchase = request.env['anggit.purchase'].sudo().search(domain, limit=limit)

        data = []
        for rec in anggit_purchase:
            products = []
            for product in rec.anggit_purchase_line_ids:
                products.append({
                    'id': product.id,
                    'nama' : product.product_id.name or '-',
                    'price' : product.price,
                    'quantity' : product.quantity,
                    'subtotal' : product.subtotal
                })

            data.append({
                'id' : rec.id,
                'partner_id' : rec.partner_id.name,
                'deskripsi' : rec.name,
                'tanggal' : rec.tanggal.strftime('%Y-%m-%d'),
                'invoice' : rec.invoice,
                'total' : rec.total,
                'status' : rec.status,
                'products' : products
            })

        return Response(
            json.dumps({'ok': True, 'count': len(data), 'data': data}),
            headers=[('Content-Type', 'application/json')]
        )
    
    @http.route('/api/anggit_purchase/<int:purchase_id>', type="http", auth='none', methods=['GET'], csrf=False)
    def detail_anggit_purchase(self, purchase_id, **params):
        auth_header = request.httprequest.headers.get('Authorization')
        user = validate_bearer_token(auth_header)

        anggit_purchase = request.env['anggit.purchase'].sudo().browse(purchase_id)
        if not anggit_purchase.exists():
            return Response(
                json.dumps({'ok': False, 'error': 'Data pembelian dengan id %d tidak ditemukan.' % purchase_id}),
                status=404,
                headers=[('Content-Type', 'application/json')]
            )
        
        if anggit_purchase.user_id.id != user.id:
            return Response(
                json.dumps({'ok': False, 'error': 'Anda tidak memiliki akses ke data ini.'}),
                status=403,
                headers=[('Content-Type', 'application/json')]
            )
        
        products = []
        for product in anggit_purchase.anggit_purchase_line_ids:
            products.append({
                'id' : product.id,
                'nama' : product.product_id.name or '-',
                'price' : product.price,
                'quantity' : product.quantity,
                'subtotal' : product.subtotal
            })
        
        data = {
            'id' : anggit_purchase.id,
            'partner_id' : anggit_purchase.partner_id.name,
            'deskripsi' : anggit_purchase.name,
            'tanggal' : anggit_purchase.tanggal.strftime('%Y-%m-%d'),
            'invoice' : anggit_purchase.invoice,
            'total' : anggit_purchase.total,
            'status' : anggit_purchase.status,
            'products' : products
        }

        print('testing4')

        return Response(
            json.dumps({'ok': True, 'data': data}),
            headers=[('Content-Type', 'application/json')]
        )

    @http.route('/api/anggit_purchase', type='http', auth='public', methods=['POST'], csrf=False)
    def create_anggit_purchase(self, **params):
        try:
            body = json.loads(request.httprequest.data)
        except Exception:
            return Response(
            json.dumps({'ok': False, 'error': 'Invalid JSON format.'}),
            status=400,
            headers=[('Content-Type', 'application/json')]
        )

        purchase_vals = {
            'partner_id' : int(body.get('partner_id', 0)) or None,
            'name' : body.get('deskripsi'),
            'tanggal' : body.get('tanggal'),
            'invoice' : body.get('invoice', '/'),
            'status' : body.get('status', 'draft')
        }

        product_items = body.get('products', [])
        product_vals = []
        for item in product_items:
            product_vals.append((0, 0, {
                'product_id' : int(item.get('product_id', 0)),
                'quantity' : float(item.get('quantity', 1)),
                'price' : float(item.get('price', 0)),
                'subtotal' : float(item.get('subtotal', 0))
            }))
        
        purchase_vals['anggit_purchase_line_ids'] = product_vals

        try:
            new_rec = request.env['anggit.purchase'].sudo().create(purchase_vals)
        except Exception as e:
            return Response(
                json.dumps({'ok': False, 'error': str(e)}),
                status=400,
                headers=[('Content-Type', 'application/json')]
            )
        
        return Response(
            json.dumps({'ok': True, 'id': new_rec.id, 'message': 'Data pembelian berhasil dibuat'}),
            status=201,
            headers=[('Content-Type', 'application/json')]
        )
    
    @http.route('/api/anggit_purchase/<int:purchase_id>', type='http', auth='public', methods=['PUT'], csrf=False)
    def update_anggit_purchase(self, purchase_id, **params):
        try:
            body = json.loads(request.httprequest.data)
        except Exception:
            return Response(
            json.dumps({'ok': False, 'error': 'Invalid JSON format.'}),
            status=400,
            headers=[('Content-Type', 'application/json')]
        )

        anggit_purchase = request.env['anggit.purchase'].sudo().browse(purchase_id)
        if not anggit_purchase.exists():
            return Response(
                json.dumps({'ok': False, 'error': 'Data pembelian dengan id %d tidak ditemukan.' % purchase_id}),
                status=404,
                headers=[('Content-Type', 'application/json')]
            )
        
        # Update data (hanya kirim field yang ingin diubah)
        purchase_fields = {}
        if 'partner_id' in body:
            purchase_fields['partner_id'] = int(body['partner_id']) or None
        if 'deskripsi' in body:
            purchase_fields['name'] = body['deskripsi']
        if 'tanggal' in body:
            purchase_fields['tanggal'] = body['tanggal']
        if 'invoice' in body:
            purchase_fields['invoice'] = body['invoice']
        if 'status' in body:
            purchase_fields['status'] = body['status']
        if 'products' in body:
            # hapus dulu data product line lama → (2, ID, 0)
            line_cmds = [(2, product.id, 0) for product in anggit_purchase.anggit_purchase_line_ids]
            for item in body['products']:
                prod_id = int(item.get('product_id', 0))
                quantity = float(item.get('quantity', 1))
                price = float(item.get('price', 0))
                subtotal = quantity * price
                line_cmds.append((0, 0, {
                    'product_id' : prod_id,
                    'quantity' : quantity,
                    'price' : price,
                    'subtotal' : subtotal
                }))
            purchase_fields['anggit_purchase_line_ids'] = line_cmds

            # commit update
        try:
            anggit_purchase.write(purchase_fields)
        except Exception as e:
            return Response(
                json.dumps({'ok': False, 'error': str(e)}),
                status=400,
                headers=[('Content-Type', 'application/json')]
            )
            
        return Response(
            json.dumps({'ok': True, 'id': anggit_purchase.id, 'message': 'Data pembelian berhasil diperbarui'}),
            headers=[('Content-Type', 'application/json')]
        )

    @http.route('/api/anggit_purchase/<int:purchase_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def delete_anggit_purchase(self, purchase_id,**params):
        anggit_purchase = request.env['anggit.purchase'].sudo().browse(purchase_id)
        if not anggit_purchase.exists():
            return Response(
                json.dumps({'ok': False, 'error': 'Data pembelian dengan id %d tidak ditemukan.' % purchase_id}),
                status=404,
                headers=[('Content-Type', 'application/json')]
            )
        
        try:
            anggit_purchase.unlink()
        except Exception as e:
            return Response(
                json.dumps({'ok': False, 'error': str(e)}),
                status=400,
                headers=[('Content-Type', 'application/json')]
            )
        
        return Response(
            json.dumps({'ok': True, 'message': 'Data pembelian berhasil dihapus'}),
            headers=[('Content-Type', 'application/json')]
        )
