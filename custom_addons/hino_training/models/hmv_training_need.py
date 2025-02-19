# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class TrainingNeed(models.Model):
    _name = 'hmv.training.need'
    _description = 'Training Need Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(
        string='Training Need No.',
        required=True,
        readonly=False,
        tracking=True,
        copy=False,
        help="Số của nhu cầu đào tạo, prefix: TN, sequence: 4 digits"
    )
    
    employee_id = fields.Many2one(
        'hr.employee',
        string='Created by',
        required=True,
        readonly=True,
        default=lambda self: self.env.user.employee_id,
        tracking=True,
        help="Người tạo phiếu"
    )
    
    assignee_id = fields.Many2one(
        'hr.employee',
        string='Assignee',
        default=lambda self: self.env.user.employee_id,
        tracking=True,
        help="Người được giao việc hoàn thành thông tin"
    )
    
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        required=True,
        readonly=True,
        related='employee_id.department_id',
        store=True,
        tracking=True
    )
    
    registration_date = fields.Date(
        string='Registration Date',
        required=True,
        readonly=True,
        default=fields.Date.context_today,
        tracking=True,
        help="Ngày tạo nhu cầu đào tạo"
    )
    
    # Tạm thời đổi thành Char thay vì Many2one
    training_brochure_id = fields.Char(
        string='Training Course Plan',
        required=True,
        tracking=True,
        help="Kế hoạch đào tạo gốc"
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
        tracking=True
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('done', 'Done')
    ], string='State', default='draft', tracking=True)
    
    description = fields.Text(
        string='Description', 
        tracking=True,
        help="Diễn giải"
    )
    
    # One2many fields for tabs
    company_line_ids = fields.One2many(
        'hmv.training.need.company',
        'training_need_id',
        string='Company Training Lines'
    )

    factory_line_ids = fields.One2many(
        'hmv.training.need.factory',
        'training_need_id',
        string='Factory Training Lines'
    )

    other_line_ids = fields.One2many(
        'hmv.training.need.other',
        'training_need_id',
        string='Other Training Lines'
    )

    approval_line_ids = fields.One2many(
        'hmv.training.need.approval',
        'training_need_id',
        string='Approval History'
    )

    # Sequence generation
    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hmv.training.need') or 'TN0001'
        return super(TrainingNeed, self).create(vals)

    # Button methods
    def action_edit(self):
        """Allow editing when in draft or rejected state"""
        self.ensure_one()
        if self.state in ['draft', 'rejected']:
            return True
        return False

    def action_save(self):
        """Save the record if in draft state"""
        self.ensure_one()
        if self.state == 'draft':
            return True
        return False

    def action_send_email(self):
        """Send notification email to assignee"""
        self.ensure_one()
        if self.assignee_id and self.assignee_id.work_email:
            template = self.env.ref('hino_training.email_template_training_need_notification')
            template.send_mail(self.id, force_send=True)
            
            
            
            
#region 1.3.2 Phê duyệt yêu cầu

    def _get_next_approver(self):
        """Get next approver based on current state and employee position"""
        # self.ensure_one()
        # employee = self.employee_id
        # job_position = employee.job_id.name if employee.job_id else False
        
        # approval_flow = {
        #     'Staff': ['Manager', 'Senior Manager', 'DGM', 'GM', 'Officer', 'HR Manager'],
        #     'Manager': ['Senior Manager', 'DGM', 'GM', 'Officer', 'HR Manager'],
        #     'Senior Manager': ['DGM', 'GM', 'Officer', 'HR Manager'],
        #     'DGM': ['GM', 'Officer', 'HR Manager'],
        #     'GM': ['Officer', 'HR Manager'],
        #     'Officer': ['HR Manager'],
        #     'HR Manager': []
        # }
        
        # current_flow = approval_flow.get(job_position, [])
        # if not current_flow:
        #     return False
            
        # return self.env['hr.employee'].search([
        #     ('job_id.name', '=', current_flow[0])
        # ], limit=1)

    def action_submit(self):
        """Submit for approval"""
        # self.ensure_one()
        # next_approver = self._get_next_approver()
        # if next_approver:
        #     self.write({
        #         'state': 'submitted',
        #     })
        #     # Create approval history record
        #     self.env['hmv.training.need.approval'].create({
        #         'training_need_id': self.id,
        #         'employee_id': next_approver.id,
        #         'status': 'waiting'
        #     })
        #     # Send notification email
        #     self._notify_next_approver(next_approver)
        # return True

    def action_approve(self):
        """Approve the training need"""
        # self.ensure_one()
        # current_user_employee = self.env.user.employee_id
        # current_approval = self.approval_line_ids.filtered(
        #     lambda r: r.employee_id == current_user_employee and r.status == 'waiting'
        # )
        
        # if current_approval:
        #     current_approval.write({
        #         'status': 'approved',
        #         'comment': 'Approved'
        #     })
            
        #     next_approver = self._get_next_approver()
        #     if next_approver:
        #         self.env['hmv.training.need.approval'].create({
        #             'training_need_id': self.id,
        #             'employee_id': next_approver.id,
        #             'status': 'waiting'
        #         })
        #         self._notify_next_approver(next_approver)
        #     else:
        #         self.write({'state': 'approved'})
        # return True

    def action_reject(self):
        """Reject the training need"""
        # self.ensure_one()
        # current_user_employee = self.env.user.employee_id
        # current_approval = self.approval_line_ids.filtered(
        #     lambda r: r.employee_id == current_user_employee and r.status == 'waiting'
        # )
        
        # if current_approval:
        #     current_approval.write({
        #         'status': 'refused',
        #         'comment': 'Rejected'
        #     })
        #     self.write({'state': 'rejected'})
        # return True

    def _notify_next_approver(self, approver):
        """Send notification to next approver"""
        # if approver.work_email:
        #     template = self.env.ref('hino_training.email_template_next_approver_notification')
        #     template.send_mail(self.id, force_send=True)
            
            
#endregion