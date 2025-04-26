# -*- coding: utf-8 -*-
{
    'name': 'Custom Invoice Report',
    'version': '1.0',
    'author': 'Sone',
    'category': 'Accounting',
    'depends': ['account'],
    'description': """
Custom Invoice Report Template
================================
This module customizes the invoice report layout.
""",
    'data': [
        'report/custom_invoice_templates.xml',
    ],
    'installable': True,
    'application': False,
}
