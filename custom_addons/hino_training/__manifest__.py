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
    'depends': ['base', 'hr', 'mail', 'purchase','web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        # report
        'report/hmv_application_report.xml',
        'report/hmv_training_courses_report.xml',
        'report/hmv_training_plan_detail_report.xml',
        'report/hmv_training_plan_summary_report.xml',
  
        # data,
        'data/hmv_training_sequence.xml',
    
        # views
        'views/hmv_training_brochure_views.xml',
        'views/hmv_training_need_views.xml',
        'views/hmv_trainning_plan_views.xml',
        'views/hmv_training_courses_views.xml',
        'views/hmv_application_views.xml',
        'views/hino_training_menus.xml',

        # Chỗ import wizard
        'wizard/hmv_training_brochure_wizard_views.xml',
        'wizard/hmv_training_courses_approval_wizard_views.xml',
        'wizard/hmv_training_need_comment_wizard_views.xml',
        'wizard/hmv_training_plan_comment_wizard_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/department_data.xml',
        'demo/job_data.xml',
        'demo/user_data.xml',
        'demo/training_data.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 1,
}
# -*- coding: utf-8 -*-
