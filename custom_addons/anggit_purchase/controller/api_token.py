from odoo import models, fields

class ApiToken(models.Model):
    _name = 'api.token'
    _description = 'API Token'

    user_id = fields.Many2one('res.users', required=True, ondelete='cascade')
    token = fields.Char(string='Token', required=True, index=True)
    expires_at = fields.Datetime(string='Expires At')