# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import Warning


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    '''
    '''
    def get_advance_lines(self, contract_id):
        payslip_advance_obj = self.env['hr.payslip.advance']
        payslip_advances = payslip_advance_obj.search([
            ('contract_id', '=', contract_id),
            ('state', '=', 'approved')
        ])

        amount = 0

        for advance in payslip_advances:
            for refund in advance.payslip_refund_ids.filtered(lambda x: x.refunded == False):
                amount = amount + refund.amount

                if not refund.payslip_id:
                    refund.write({
                        'payslip_id': self.id
                    })

                break
        
        return [[5, 0, 0], [0, 0, {
            'name': 'Total Advances',
            'code': 'ADL',
            'amount': amount * -1,
            'payslip_id': self.id,
            'contract_id': self.contract_id.id,
            'sequence': 100
        }]]

    @api.multi
    def compute_sheet(self):
        self.write({
            'input_line_ids': self.get_advance_lines(self.contract_id.id)
        })

        return super(HrPayslip, self).compute_sheet()

    @api.multi
    def hr_verify_sheet(self):
        result = super(HrPayslip, self).hr_verify_sheet() 
        
        domain = [('payslip_id', '=', self.id)]
        payslip_advance_refund = self.env['hr.payslip.advance.refund'].search(domain)

        for refund in payslip_advance_refund:
            refund.write({
                'refunded': True
            })

        return result

    @api.multi
    def cancel_sheet(self):
        domain = [('payslip_id', '=', self.id)]
        payslip_advance_refund_obj = self.env['hr.payslip.advance.refund']
        payslip_advance_refund = payslip_advance_refund_obj.search(domain)

        for refund in payslip_advance_refund:
            refund.write({
                'refunded': False
            })

        return super(HrPayslip, self).cancel_sheet()
