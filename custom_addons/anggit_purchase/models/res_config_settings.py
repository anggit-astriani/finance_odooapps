from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    payable_account_code = fields.Many2one(
        'account.account',
        string='Payable Account Code',
        config_parameter='anggit_purchase.payable_account_code',
        domain=[('account_type', '=', 'liability_payable')],
        # default='21100011',
        help='Kode akun hutang untuk vendor bill (contoh: 21100011)',
    )

    expense_account_code = fields.Many2one(
        'account.account',
        string='Expense Account Code',
        config_parameter='anggit_purchase.expense_account_code',
        domain=[('account_type', '=', 'expense_direct_cost')],
        # default='51000011',
        help='Kode akun beban untuk baris vendor bill (contoh: 51000011)',
    )