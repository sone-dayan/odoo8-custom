# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)

class HrPayslipAdvance(models.Model):
    _name = 'hr.payslip.advance'
    _description = 'Salary Advance'

    number = fields.Char(string='Advance Number', required=True, default='/', readonly=True)
    description = fields.Char(string='Short Description')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    contract_id = fields.Many2one('hr.contract', string='Contract')
    date = fields.Date(string='Date', default=fields.Date.today)
    amount = fields.Float(string='Amount', required=True)
    generate_lines = fields.Boolean(string='Generate Lines')
    monthly_amount = fields.Float(string='Monthly Repayment Amount')
    repayment_start_date = fields.Date(string='Repayment Start Date')
    note = fields.Text(string='Note')
    reimburse_monthly = fields.Boolean(string='Reimburse Monthly', default=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded')
    ], string='Status', default='draft', track_visibility='onchange')

    line_ids = fields.One2many('hr.payslip.advance.line', 'advance_id', string='Repayment Plan')

    def action_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)

    def action_approve(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return self.write(cr, uid, ids, {'state': 'approved'}, context=context)
    
    def action_disapprove(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def action_paid(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return self.write(cr, uid, ids, {'state': 'paid'}, context=context)

    def action_refund(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.write(cr, uid, ids, {'state': 'refunded'}, context=context)
        for record in self.browse(cr, uid, ids, context=context):
            line_ids = [line.id for line in record.line_ids]
            self.pool.get('hr.payslip.advance.line').write(cr, uid, line_ids, {'state': 'refunded'}, context=context)
        return True

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        # Generate sequence if not set
        if vals.get('number', '/') == '/':
            vals['number'] = self.pool.get('ir.sequence').get(cr, uid, 'salary.advance')

        record_id = super(HrPayslipAdvance, self).create(cr, uid, vals, context=context)
        record = self.browse(cr, uid, record_id, context=context)

        if record.generate_lines and record.reimburse_monthly and \
           record.repayment_start_date and record.monthly_amount > 0:
            self._generate_repayment_lines(cr, uid, [record_id], context=dict(context, skip_line_generation=True))

        return record_id

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}

        res = super(HrPayslipAdvance, self).write(cr, uid, ids, vals, context=context)

        if context.get('skip_line_generation'):
            return res

        for record in self.browse(cr, uid, ids, context=context):
            if record.generate_lines and record.reimburse_monthly and \
               record.repayment_start_date and record.monthly_amount > 0:
                self._generate_repayment_lines(cr, uid, [record.id], context=dict(context, skip_line_generation=True))

        return res

    def _generate_repayment_lines(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        line_obj = self.pool.get('hr.payslip.advance.line')
        for advance in self.browse(cr, uid, ids, context=context):
            # Clear existing lines
            if advance.line_ids:
                line_obj.unlink(cr, uid, [line.id for line in advance.line_ids], context=context)

            # Validations
            if not advance.generate_lines or not advance.reimburse_monthly:
                continue
            if not advance.repayment_start_date:
                raise Warning(_("Repayment start date must be set."))
            if not advance.monthly_amount or advance.monthly_amount <= 0:
                raise Warning(_("Monthly repayment amount must be greater than zero."))
            if not advance.amount or advance.amount <= 0:
                raise Warning(_("Advance amount must be greater than zero."))
            if advance.monthly_amount > advance.amount:
                raise Warning(_("Monthly repayment amount cannot exceed the total advance amount."))

            total_months = int(advance.amount / advance.monthly_amount)
            remaining = round(advance.amount - (advance.monthly_amount * total_months), 2)

            start_date = datetime.strptime(advance.repayment_start_date, "%Y-%m-%d").date()
            current_date = start_date

            valid_line_states = ['draft','confirmed', 'paid', 'refunded']
            line_state = advance.state if advance.state in valid_line_states else 'paid'

            lines_data = []

            for i in range(total_months):
                lines_data.append({
                    'date': current_date.strftime("%Y-%m-%d"),
                    'amount': advance.monthly_amount,
                    'state': line_state,
                    'advance_id': advance.id,
                })
                current_date += relativedelta(months=1)

            if remaining > 0.01:
                lines_data.append({
                    'date': current_date.strftime("%Y-%m-%d"),
                    'amount': remaining,
                    'state': line_state,
                    'advance_id': advance.id,
                })

            for line_vals in lines_data:
                line_obj.create(cr, uid, line_vals, context=context)

            _logger.info("Generated %s repayment lines for advance ID %s", len(lines_data), advance.id)

class HrPayslipAdvanceLine(models.Model):
    _name = 'hr.payslip.advance.line'

    advance_id = fields.Many2one('hr.payslip.advance', string="Advance", ondelete='cascade', required=True)
    date = fields.Date('RePayment Date')
    amount = fields.Float('Amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ], 'State', readonly=True, default='draft')
    payslip_id = fields.Many2one('hr.payslip', string="Payslip")
