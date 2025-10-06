from odoo import models, fields, _

class product_template(models.Model):
    _inherit = "product.template"
    
    product_description = fields.Char(string="Product Description")