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

        # templates
        'templates/training_plan_tab_factory_training.xml', 
        'templates/training_plan_report_template.xml',
        'templates/hmv_training_courses_report.xml',
        'templates/application_report_template.xml',
  
        # data,
        'data/sequence.xml',
        'data/department_data.xml',
        'data/job_data.xml',
        'data/user_data.xml',
    
        # views
        'views/hmv_training_brochure.xml',
        'views/hmv_training_courses_form_view.xml',
        'views/hmv_training_need_view.xml',
        'views/trainning_plan_view.xml',
        'views/application.xml',
        'views/menu.xml',

        # Chỗ import wizard
        'wizard/training_need_comment_wizard_view.xml',
        'wizard/training_courses_approval_wizard_view.xml',
        'wizard/training_plan_comment_wizard_view.xml',
        'wizard/hmv_training_brochure_wizard.xml',
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
# -*- coding: utf-8 -*-
