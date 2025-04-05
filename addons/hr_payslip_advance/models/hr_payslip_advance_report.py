# -*- coding: utf-8 -*-
from openerp import models, api
from openerp.exceptions import Warning

class HrPayslipAdvanceReport(models.AbstractModel):
    _name = 'report.hr_payslip_advance.hr_payslip_advance_refund_report'
    _report_name = 'hr_payslip_advance.hr_payslip_advance_refund_report'
    _model_name = 'hr.payslip'

    '''
    '''
    @api.model
    def get_advance_lines(self, payslip_id):
        domain = [
            ('payslip_id', '=', payslip_id),
            ('refunded', '=', True)
        ]
        advance_refund_obj = self.env['hr.payslip.advance.refund']

        return advance_refund_obj.search(domain)

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(self._report_name)

        payslip_obj = self.env[self._model_name]
        payslips = payslip_obj.browse(self.ids)

        for payslip in payslips:
            if payslip.state != 'done':
                raise Warning('There are no processed payslips available to print advance records.')


        values = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'payslips': payslips
        }

        return self.env['report'].render(self._report_name, values)
