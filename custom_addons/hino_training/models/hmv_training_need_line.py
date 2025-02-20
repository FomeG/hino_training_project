# -*- coding: utf-8 -*-
from odoo import models, fields, api

class TrainingNeedCompanyTab(models.Model):
    _name = 'hmv.training.need.company'
    _description = 'Training Courses Provided By Company Tab'

    training_need_id = fields.Many2one(
        'hmv.training.need',
        string='Training Need',
        ondelete='cascade'
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Full Name',
        required=True,
        domain="[('department_id', '=', parent.department_id), ('active', '=', False)]"
    )
    
    email = fields.Char(
        string='Email',
        required=True,
        related='employee_id.work_email',
        readonly=True
    )
    
    training_brochure_line_id = fields.Many2one(
        'hmv.training.brochure.line',
        string='Courses',
        required=True,
        domain="[('training_brochure_id', '=', parent.training_brochure_id), ('training_type', '=', 'company')]"
    )








class TrainingNeedFactoryTab(models.Model):
    _name = 'hmv.training.need.factory'
    _description = 'Factory Training Tab'

    training_need_id = fields.Many2one(
        'hmv.training.need',
        string='Training Need',
        ondelete='cascade'
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Full Name',
        required=True,
        domain="[('department_id', '=', parent.department_id), ('active', '=', False)]"
    )
    
    email = fields.Char(
        string='Email',
        required=True,
        related='employee_id.work_email',
        readonly=True
    )
    
    # Tạm thời đổi thành Char thay vì Many2many
    training_plan_line_id = fields.Char(
        string='Courses',
        required=True,
        help="Temporary field for courses"
    )







class TrainingNeedOtherTab(models.Model):
    _name = 'hmv.training.need.other'
    _description = 'Other Training Tab'

    training_need_id = fields.Many2one(
        'hmv.training.need',
        string='Training Need',
        ondelete='cascade'
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Full Name',
        required=True,
        domain="[('department_id', '=', parent.department_id), ('active', '=', False)]"
    )
    
    email = fields.Char(
        string='Email',
        required=True,
        related='employee_id.work_email',
        readonly=True
    )
    
    # Tạm thời đổi thành Char thay vì Many2many
    training_plan_line_id = fields.Char(
        string='Courses',
        required=True,
        help="Temporary field for courses"
    )








class TrainingNeedApprovalHistory(models.Model):
    _name = 'hmv.training.need.approval'
    _description = 'Approval History Tab'
    _order = 'id asc'

    training_need_id = fields.Many2one(
        'hmv.training.need',
        string='Training Need',
        ondelete='cascade'
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Approver',
        help="Tên người trong luồng phê duyệt"
    )
    
    job_id = fields.Many2one(
        'hr.job',
        string='Position',
        related='employee_id.job_id',
        store=True,
        help="Vị trí của người trong luồng phê duyệt"
    )
    
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True,
        help="Phòng ban của người trong luồng phê duyệt"
    )
    
    status = fields.Selection([
        ('waiting', 'Waiting to approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused')
    ], string='Status', default='waiting',
       help="Waiting to approve: Chưa duyệt\nApproved: Đã duyệt\nRefused: Từ chối")
    
    comment = fields.Text(
        string='Comment',
        help="Lưu lại comment của approver khi approve/refuse"
    )