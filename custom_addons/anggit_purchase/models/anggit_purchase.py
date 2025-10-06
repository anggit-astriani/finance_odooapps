from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError

class anggit_purchase(models.Model):
    _name = "anggit.purchase"

    invoice = fields.Char(string="Invoice", default="/")
    name = fields.Char(string='Deskripsi')
    partner_id = fields.Many2one('res.partner', string="Partner", required=True)
    tanggal = fields.Date(string='Tanggal')
    status = fields.Selection(
        [
            ('draft','Draft'),
            ('approve','Approve'),
            ('done','Done')
        ],
        string="Status", default='draft', tracking=True
    )
    anggit_purchase_line_ids = fields.One2many('anggit.purchase.line', 'anggit_purchase_id', string="Anggit Purchase Line Ids")
    anggit_category = fields.Many2many('anggit.category', 'anggit_purchase_category_rel', 'anggit_purchase_id', 'anggit_category_id', string="Kategori")
    total = fields.Float(string="Total", compute="_compute_total", store=True)
    vendor_bill_id = fields.Many2one('account.move', String="Vendor Bill", readonly=True, copy=False)
    # journal_entry_id = fields.Many2one('account.move', string='Journal Entry', readonly=True, copy=False)

    @api.depends('anggit_purchase_line_ids.subtotal')
    def _compute_total(self):
        for record in self:
            record.total = sum(line.subtotal for line in record.anggit_purchase_line_ids)

    def funct_approve(self):
        if self.status == 'draft':
            if self.invoice == '/':
                seq = self.env['ir.sequence'].next_by_code('invoice_sequence') or '/'
                self.invoice = seq
            self.status = 'approve'

    # def funct_set_to_done(self):
    #     for record in self:
    #         if record.status == 'approve':
    #             record.status = 'done'
    #             record.create_journal_entry()

    def funct_set_to_done(self):
        for rec in self:
            if rec.status != 'approve':
                continue
            rec.status = 'done'
            # 1. buat vendor bill draft
            rec.create_vendor_bill()
            # 2. buat journal entry
            # rec.create_journal_entry()

    @api.model
    def create(self, values):
        res = super(anggit_purchase, self).create(values)
        
        for rec in res:
            if not rec.name:
                raise ValidationError(_("Nama tidak boleh kosong"))

            tanggal_purchase = rec.tanggal
            tanggal_sekarang = date.today()
            if tanggal_purchase < tanggal_sekarang:
                raise ValidationError(_("Tanggal tidak boleh kurang dari tanggal sekarang"))
        return res

    def write(self, values):
        res = super(anggit_purchase, self).write(values)

        for rec in self:
            if not rec.name:
                raise ValidationError(_("Nama tidak boleh kosong"))

            if 'tanggal' in values:
                tanggal_purchase = self.tanggal
                tanggal_sekarang = date.today()
                if tanggal_purchase < tanggal_sekarang:
                    raise ValidationError(_("Tanggal tidak boleh kurang dari tanggal sekarang"))
        return res
    
    # ---------- method bantuan ----------
    # def _get_account(self, code):
    #     """Cari account untuk company saat ini."""
    #     acc = self.env['account.account'].search([
    #         ('code', '=', code),
    #         ('company_id', '=', self.env.company.id)
    #     ], limit=1)
    #     if not acc:
    #         raise UserError(_('Account %s tidak ditemukan untuk company %s')
    #                       % (code, self.env.company.name))
    #     return acc

    def _get_param_account(self, param_key):
        """Ambil account berdasarkan kode yang tersimpan di ir.config_parameter."""
        account_id = (self.env['ir.config_parameter']
                .sudo()
                .get_param(param_key))
        if not account_id:
            raise UserError(
                _('System parameter %s belum di-set. Hubungi administrator.') % param_key
            )
        
        account = self.env['account.account'].browse(int(account_id))
        if not account:
            raise UserError(
                _('Account dengan kode %s tidak ditemukan untuk company %s')
                % (account_id, self.env.company.name)
            )
        return account
    
    def _prepare_vendor_bill_vals(self):
        """Return dict untuk membuat vendor bill draft."""
        self.ensure_one()
        journal = self.env['account.journal'].search([
            ('type', '=', 'purchase'),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        if not journal:
            raise UserError(_('Tidak ada journal tipe "purchase" untuk company ini.'))

        # pilih akun hutang (payable) dari partner / atau default
        # payable_acc = self._get_account('21100011')
        payable_acc = self._get_param_account('anggit_purchase.payable_account_code')

        invoice_line_vals = []
        for line in self.anggit_purchase_line_ids:
            # expense_acc = self._get_account('51000011')
            expense_acc = self._get_param_account('anggit_purchase.expense_account_code')
            invoice_line_vals.append((0, 0, {
                'product_id'     : line.product_id.id,
                'name'           : line.description or line.product_id.name,
                'quantity'       : line.quantity,
                'product_uom_id' : line.uom_id.id,
                'price_unit'     : line.price,
                'account_id'     : expense_acc.id,
                'tax_ids'        : [(6, 0, [])],
            }))

        return {
            'move_type'  : 'in_invoice',
            'partner_id' : self.partner_id.id,
            'invoice_date': self.tanggal or fields.Date.today(),
            'journal_id' : journal.id,
            'invoice_line_ids': invoice_line_vals,
            'ref' : self.invoice or self.name,
            'line_ids': [
                (0, 0, {
                    'account_id': payable_acc.id,
                    'partner_id': self.partner_id.id,
                    'credit': sum(line.subtotal for line in self.anggit_purchase_line_ids),
                    'debit': 0,
                }) for line in self.anggit_purchase_line_ids]
        }

    def create_vendor_bill(self):
        """Buat vendor bill (draft) dan simpan ID-nya."""
        self.ensure_one()
        if self.vendor_bill_id:
            raise UserError(_('Vendor bill sudah pernah dibuat.'))
        vals = self._prepare_vendor_bill_vals()
        bill = self.env['account.move'].create(vals)
        self.vendor_bill_id = bill
        return bill
    
    # untuk membuat journal entry
    # def _get_purchase_journal(self):
    #     """Ambil / buat journal tipe 'purchase'."""
    #     journal = self.env['account.journal'].search([
    #         ('type', '=', 'purchase'),
    #         ('company_id', '=', self.env.company.id)
    #     ], limit=1)
    #     if not journal:
    #         journal = self.env['account.journal'].create({
    #             'name': 'Vendor Bills',
    #             'type': 'purchase',
    #             'code': 'PUR',
    #             'company_id': self.env.company.id,
    #         })
    #     return journal

    # def create_journal_entry(self):
    #     """Buat journal entry Dr COGS, Cr Payable."""
    #     self.ensure_one()
    #     if self.journal_entry_id:
    #         raise UserError(_('Journal entry sudah ada.'))

    #     cogs_acc   = self._get_account('51000010')
    #     payable_acc= self._get_account('21100010')
    #     total      = self.total or 0.0

    #     move_vals = {
    #         'ref': self.invoice or self.name,
    #         'date': self.tanggal or fields.Date.today(),
    #         'journal_id': self._get_purchase_journal().id,
    #         'move_type': 'entry',
    #         'partner_id': False,
    #         'line_ids': [
    #             (0, 0, {
    #                 'account_id': cogs_acc.id,
    #                 'name': 'COGS - %s' % (self.name or ''),
    #                 'debit': total,
    #                 'credit': 0.0,
    #             }),
    #             (0, 0, {
    #                 'account_id': payable_acc.id,
    #                 'name': 'Trade Payable - %s' % (self.name or ''),
    #                 'debit': 0.0,
    #                 'credit': total,
    #             }),
    #         ],
    #     }
    #     move = self.env['account.move'].create(move_vals)
    #     move.action_post()
    #     self.journal_entry_id = move
    #     return move
