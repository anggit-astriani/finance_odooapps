from odoo import models, fields, api, _

class anggit_purchase_line(models.Model):
    _name = "anggit.purchase.line"

    anggit_purchase_id = fields.Many2one('anggit.purchase', string="Anggit Purchase Id")
    product_id = fields.Many2one('product.product', string="Product Id")
    quantity = fields.Float(string="Quantity", default=0)
    uom_id = fields.Many2one('uom.uom', string="Satuan")
    description = fields.Char(string="Description")
    price = fields.Float(string="Harga", default=0.0)
    subtotal = fields.Float(string="Sub Total", compute="_funct_subtotal", store=True)

    @api.onchange('product_id')
    def funct_onchange_product_id(self):
        if not self.product_id:
            return {}
        else:
            self.description = 'Desc - ' + self.product_id.name
            self.price = self.product_id.list_price
        return {}
    
    @api.depends('quantity', 'price')
    def _funct_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price

