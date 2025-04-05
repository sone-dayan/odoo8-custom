# -*- coding: utf-8 -*-
from openerp import models, fields

class HrContract(models.Model):
    _inherit = 'hr.contract'

    payslip_advance_limit = fields.Float(digits=(10, 2), string='Advance Limit')