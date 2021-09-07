# -*- coding: utf-8 -*-
{
    'name': "ODOO-MOODLE INTERFACE",

    'summary': """
        This module conects wihth moodle app for registering students 
        in Academia programs""",

    'description': """
        This module conects ODOO with moodle for registering students in
        Transformacion Genial / Academia programs. It uses the moodle api to 
        access moodle and create students. 
        
        Colaborador: Jose Angel Eduardo
    """,

    'author': "CIEXPRO",
    'website': "https://www.ciexpro.com",
    'sequence': 1,
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Education',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'base_setup',
                'openeducat_core',
                'mail',
                'contacts',
                'l10n_ve_banks'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/student_odoo_moodle_view.xml',
        'data/moodle_odoo_parameters_data.xml',
        'data/course_payment_platform_data.xml',
        'views/mail_template.xml',
        'views/course_view.xml',
    ],
    # only loaded in demonstration mode
    #'demo': [
    #    'demo/demo.xml',
    #],
}
