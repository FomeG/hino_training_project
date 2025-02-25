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
    'depends': ['base', 'hr', 'mail', 'purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/application/application.xml',

        'data/sequence.xml',
        'views/trainning_plan_view.xml',

        'views/views.xml',

        'data/hmv_need_sequence.xml',
        'data/sequence.xml',
        'data/department_data.xml',
        'data/job_data.xml',
        'data/user_data.xml',

        'views/hmv_training_need_view.xml',

        'views/hmv_training_brochure.xml',
        'views/hmv_training_courses_form_view.xml',
        'views/test.xml',
        'views/menu.xml',

        'views/hmv_training_brochure.xml',
        'views/hmv_training_courses_form_view.xml',

        'templates/application_report_template.xml',
        # 'views/application/application_approval.xml',

        'views/menu.xml',
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
