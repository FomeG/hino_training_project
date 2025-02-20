# -*- coding: utf-8 -*-
{
    'name': "hino_training",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'hr', 'purchase'],

    # always loaded
    'data': [

        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/views.xml',
        'views/trainning_plan_view.xml',

        'views/action.xml',
        'views/menu.xml',
        'views/tad_Training_courses_provided_by_company.xml',

        'views/tad_Factory_training.xml',
        'views/tad_Other.xml',
        'views/tad_Approval_history.xml',
        'views/hmv_training_brochure.xml',
        'views/hmv_training_courses_form_view.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    
    
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 1,
}

