# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 8Bits Software
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'HR Payslip Advance Omamori',
    'description': 'Manage employee payslip advances',
    'author': '8Bits Software',
    'category': 'Tools',
    'version': '8.0.0.1',
    'license': 'AGPL-3','version': '8.0.0.1',
    'depends': ['account', 'hr'],
    'data': [
        'views/hr_payslip_advance_view.xml',
        'views/hr_contract_view.xml',
        'views/hr_payslip_view.xml',
        'reports/hr_payslip_advance_report.xml',
        'reports/hr_payslip_advance_refund_report.xml'
    ],
    'installable': True
}

