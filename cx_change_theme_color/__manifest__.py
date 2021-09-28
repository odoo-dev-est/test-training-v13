# -*- coding: utf-8 -*-
{
    'name': "Change Menu Theme Color",

    'summary': """
        Change color menu bar""",

    'description': """
        Change color menu bar
    """,

    'author': "CIEXPRO",
    'website': "http://www.ciexpro.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'UserInterface',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/templates.xml',
    ],
}
