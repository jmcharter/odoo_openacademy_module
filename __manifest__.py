# -*- coding: utf-8 -*-
{
    'name': "Open Academy",

    'summary': """
        Manage training modules""",

    'description': """
        Open Academy module to manage:
            - training courses
            - training sessions
            - attendee registrations
    """,

    'author': "Jon Charter",
    'website': "https://joncharter.co.uk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        # 'views/views.xml',
        'views/templates.xml',
        'views/openacademy.xml',
        'views/partner.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
