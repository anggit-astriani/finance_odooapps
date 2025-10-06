from odoo import models, fields, _

class anggit_category(models.Model):
    _name = "anggit.category"

    name = fields.Char(string="Name")