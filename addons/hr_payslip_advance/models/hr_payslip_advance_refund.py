# -*- coding: utf-8 -*-
# from openerp import api, models, fields

# class HrPayslipAdvanceRefund(models.Model):
#     _name = 'hr.payslip.advance.refund'

#     amount = fields.Float(string='Refund Amount', digits=(10, 2))
#     date = fields.Date()
#     refunded = fields.Boolean(string='Refunded', default=False)
#     payslip_advance_id = fields.Many2one(comodel_name='hr.payslip.advance')
#     payslip_id = fields.Many2one(comodel_name='hr.payslip')

from openerp import models, fields

class HrPayslipAdvanceRefund(models.Model):
    _name = 'hr.payslip.advance.refund'

    date = fields.Date(string='Date')
    amount = fields.Float(string='Amount', digits=(10, 2))
    state = fields.Selection([
        ('paid', 'Paid'),
        ('refunded', 'Refunded')
    ], string='Status', default='paid')
    payslip_advance_id = fields.Many2one('hr.payslip.advance', string='Advance')
    payslip_id = fields.Many2one('hr.payslip', string='Payslip')

