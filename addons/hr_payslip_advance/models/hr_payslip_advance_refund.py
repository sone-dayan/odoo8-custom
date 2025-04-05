# -*- coding: utf-8 -*-
from openerp import api, models, fields

class HrPayslipAdvanceRefund(models.Model):
    _name = 'hr.payslip.advance.refund'

    amount = fields.Float(string='Refund Amount', digits=(10, 2))
    date = fields.Date()
    refunded = fields.Boolean(string='Refunded', default=False)
    payslip_advance_id = fields.Many2one(comodel_name='hr.payslip.advance')
    payslip_id = fields.Many2one(comodel_name='hr.payslip')
