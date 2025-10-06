from odoo import models, fields, _

class purchase_order(models.Model):
    _inherit = "purchase.order"

    internal_notes = fields.Text(string="Internal Notes")