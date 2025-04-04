# -*- coding: utf-8 -*-
from openerp import api, models, fields
from openerp.exceptions import Warning
from datetime import date

class HrPayslipAdvance(models.Model):
    _name = 'hr.payslip.advance'

    HR_PAYSLIP_ADVANCE_STATUS = [
        ('draft', 'Borrador'),
        ('approved', 'Aprovado'),
        ('disapproved', 'Desaprobado')
    ]

    '''
    '''
    def _get_default_name(self):
        return 'ADV/%s/%d' % (date.today().year, self.search_count([]) + 1)



    name = fields.Char(string='Nombre', size=50, default=_get_default_name)
    amount = fields.Float(string='Monto', digits=(10, 2))
    date = fields.Date(string='Fecha', required=True, default=lambda self: fields.Date.today())
    state = fields.Selection(string='Estado', selection=HR_PAYSLIP_ADVANCE_STATUS, default='draft')
    reason = fields.Char(string='Motivo', size=160)
    payment_term_id = fields.Many2one(string='Términos de cobro', comodel_name='account.payment.term', required=True)
    contract_id = fields.Many2one(string='Contrato de Empleado', comodel_name='hr.contract', required=True)
    journal_id = fields.Many2one(string='Método de pago', comodel_name='account.journal', required=True)
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
            raise Warning('Límite superado de adelantos para este contrato')

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
            return Warning('No se puede modificar un adelanto aprobado')
        
        values['amount_unreconcilied'] = values.get('amount', 0)

        return super(HrPayslipAdvance, self).write(cr, uid, ids, values, context=context)

    '''
    '''
    def unlink(self, cr, uid, ids, context=None):
        payslip_advance = self.pool.get(self._name).browse(cr, uid, ids, context=context)

        if payslip_advance.state == 'approved':
            return Warning('No se puede borrar un adelando aprobado')

        return super(HrPayslipAdvance, self).unlink(cr, uid, ids, context=context)
    
    '''
    '''
    @api.one
    def action_approve(self):
        if self.state == 'approved':
            return Warning('No se puede aprobar un adelanto ya aprobado')

        if self.state == 'disapprobed':
            return Warning('No se puede aprobar un adelato no aprobado')

        return self.write({
            'amount_unreconcilied': self.amount,
            'state': 'approved'
        })

    '''
    '''
    @api.one
    def action_disapprove(self):
        if self.state == 'approved':
            return Warning('No se puede aprobar un adelanto no aprobado')

        if self.state == 'disaproved':
            return Warning('No se puede desaprobar un adelando aprobado')

        return self.write({
            'amount_unreconcilied': self.amount,
            'state': 'disapproved'
        })