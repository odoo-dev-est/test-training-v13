# -*- coding: utf-8 -*-
{
    'name': "l10n_ve_banks",

    'summary': """
        Add list of Venezuela banks""",

    'description': """
        adds a fiel to regist origin banks
    """,

    'author': "CIEXPRO",
    'website': "http://www.ciexpro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Banks',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'data/bank_list.xml',
    ],
}
