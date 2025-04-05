# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp.exceptions import Warning
from datetime import date

class HrPayslipAdvance(models.Model):
    _name = 'hr.payslip.advance'

    HR_PAYSLIP_ADVANCE_STATUS = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('disapproved', 'Disapproved'),
    ]

    '''
    '''
    def _get_default_name(self):
        return 'ADV/%s/%d' % (date.today().year, self.search_count([]) + 1)



    name = fields.Char(string='Name', size=50, default=_get_default_name)
    amount = fields.Float(string='Amount', digits=(10, 2))
    date = fields.Date(string='Date', required=True, default=lambda self: fields.Date.today())
    state = fields.Selection(string='State', selection=HR_PAYSLIP_ADVANCE_STATUS, default='draft')
    reason = fields.Char(string='Reason', size=160)
    payment_term_id = fields.Many2one(string='Payment Terms', comodel_name='account.payment.term', required=True)
    contract_id = fields.Many2one(string='Employee Contract', comodel_name='hr.contract', required=True)
    journal_id = fields.Many2one(string='Payment Method', comodel_name='account.journal', required=True)
    payslip_refund_ids = fields.One2many(comodel_name='hr.payslip.advance.refund', inverse_name='payslip_advance_id')

    '''
    '''
    def compute_payments_refund(self, payment_term_id, amount):
        payment_term = self.env['account.payment.term'].browse(payment_term_id)
        payment_term_lines = payment_term.compute(amount)

        return [[0, False, {
            'date': line[0],
            'amount': line[1]
        }] for line in payment_term_lines[0]]


    '''
    '''
    def check_advance_limit(self, contract_id, amount):
        domain = [
            ('contract_id', '=', contract_id),
            ('payslip_refund_ids.refunded', '=', False)
        ]

        advance_obj = self.env['hr.payslip.advance']
        advance = advance_obj.search(domain)
        
        total_unrefunded = 0

        if advance:
            total_unrefunded = advance.mapped(lambda x: total_unrefunded + x.amount)[0]

        if total_unrefunded > amount:
            raise Warning('Advance limit exceeded for this contract.')

    '''
    '''
    @api.model
    def create(self, values):
        amount = values.get('amount', 0)
        contract_id = values.get('contract_id', None)

        self.check_advance_limit(contract_id, amount)

        payment_term_id = values.get('payment_term_id', None)

        values['amount_unreconcilied'] = amount
        values['payslip_refund_ids'] = self.compute_payments_refund(payment_term_id, amount)

        return super(HrPayslipAdvance, self).create(values)

    '''
    '''
    def write(self, cr, uid, ids, values, context=None):
        payslip_advance = self.pool.get(self._name).browse(cr, uid, ids, context=context)

        if payslip_advance.state == 'approved':
            return Warning('You cannot modify an approved advance.')
        
        values['amount_unreconcilied'] = values.get('amount', 0)

        return super(HrPayslipAdvance, self).write(cr, uid, ids, values, context=context)

    '''
    '''
    def unlink(self, cr, uid, ids, context=None):
        payslip_advance = self.pool.get(self._name).browse(cr, uid, ids, context=context)

        if payslip_advance.state == 'approved':
            return Warning('You cannot delete an approved advance.')

        return super(HrPayslipAdvance, self).unlink(cr, uid, ids, context=context)
    
    '''
    '''
    @api.one
    def action_approve(self):
        if self.state == 'approved':
            return Warning('This advance is already approved.')

        if self.state == 'disapproved':
            return Warning('You cannot approve a disapproved advance.')

        return self.write({
            'amount_unreconcilied': self.amount,
            'state': 'approved'
        })

    '''
    '''
    @api.one
    def action_disapprove(self):
        if self.state == 'approved':
            return Warning('You cannot disapprove an approved advance.')

        if self.state == 'disapproved':
            return Warning('This advance is already disapproved.')

        return self.write({
            'amount_unreconcilied': self.amount,
            'state': 'disapproved'
        })