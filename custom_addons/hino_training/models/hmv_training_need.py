# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime

from odoo.exceptions import UserError, ValidationError

class TrainingNeed(models.Model):
    _name = 'hmv.training.need'
    _description = 'Training Need Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(
        string='Training Need No.',
        required=True,
        readonly=False,
        default=lambda self: self._get_default_code(),
        tracking=True,
        copy=False,
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
        required=False,
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
    
    # TRAINING BROCHURE
    training_brochure_id = fields.Many2one(
        'hmv.training.brochure',
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
        ('manager_approved', 'Manager Approved'),
        ('senior_manager_approved', 'Senior Manager Approved'),
        ('dgm_approved', 'DGM Approved'),
        ('gm_approved', 'GM Approved'),
        ('officer_approved', 'Officer Approved'),
        # ('hr_approved', 'HR Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed')
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

    def _get_default_code(self):
        # Lấy giá trị mặc định từ ir.sequence
        return self.env['ir.sequence'].next_by_code('hmv.training.need.code') or 'TN0001'

    
    # Sequence generation
    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self._get_default_code()
        return super(TrainingNeed, self).create(vals)

    
    
    @api.constrains('department_id', 'registration_date')
    def _check_department_yearly_need(self):
        for record in self:
            # Lấy năm từ ngày đăng ký
            year = record.registration_date.year
            
            # Tìm kiếm các training need khác của cùng phòng ban trong năm này
            domain = [
                ('department_id', '=', record.department_id.id),
                ('id', '!=', record.id),  # Loại trừ record hiện tại
                ('registration_date', '>=', f'{year}-01-01'),
                ('registration_date', '<=', f'{year}-12-31'),
                ('state', 'not in', ['rejected', 'cancel'])  # Không tính các trạng thái bị từ chối hoặc hủy
            ]
            
            existing_need = self.search_count(domain)
            
            if existing_need > 0:
                raise ValidationError(_(
                    'Your department already has a training need registration for year %s. '
                    'Only one training need per department is allowed per year.') % year
                )
                
           
    @api.depends('employee_id')
    def _compute_department_id(self):
        for record in self:
            record.department_id = record.employee_id.department_id or False     
                
                
                
    @api.onchange('training_brochure_id')
    def _onchange_training_brochure_id(self):
        """
        When training_brochure_id changes, reset all tabs by clearing their lines
        """
        # Clear all lines in the Company tab
        self.company_line_ids = [(5, 0, 0)]
        
        # Clear all lines in the Factory tab
        self.factory_line_ids = [(5, 0, 0)]
        
        # Clear all lines in the Other tab
        self.other_line_ids = [(5, 0, 0)] 
                
                
                
                
                
                
#region Button methods
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
        for record in self:
            if not record.assignee_id.work_email:
                raise ValidationError(_("Assignee must have an email address defined."))
                
            mail_values = {
                'subject': f'Training Need Assignment: {record.name}',
                'email_from': self.env.user.email or self.env.company.email,
                'email_to': record.assignee_id.work_email,
                'body_html': f"""
                    <div style="margin: 0px; padding: 0px;">
                        <p style="margin: 0px; padding: 0px; font-size: 13px;">
                            Dear {record.assignee_id.name},
                            <br/><br/>
                            You have been assigned to complete the Training Need: {record.name}
                            <br/><br/>
                            Details:
                            <ul>
                                <li>Department: {record.department_id.name}</li>
                                <li>Created by: {record.employee_id.name}</li>
                                <li>Registration Date: {record.registration_date}</li>
                                <li>Training Course Plan: {record.training_brochure_id.name}</li>
                            </ul>
                            <br/>
                            Please review and complete the required information.
                            <br/><br/>
                            Best regards,<br/>
                            {self.env.user.name}
                        </p>
                    </div>
                """
            }

            # Create and send email
            self.env['mail.mail'].create(mail_values).send()

            # Show success message
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Notification email sent to %s') % record.assignee_id.name,
                    'type': 'success',
                    'sticky': False,
                }
            }
            
    def action_send_mass_email(self):
        """Send notification emails to assignees of selected training needs"""
        for record in self:
            if not record.assignee_id.work_email:
                raise ValidationError(_(
                    "Assignee '%s' must have an email address defined.") % record.assignee_id.name
                )
                
            mail_values = {
                'subject': f'Training Need Assignment: {record.name}',
                'email_from': self.env.user.email or self.env.company.email,
                'email_to': record.assignee_id.work_email,
                'body_html': f"""
                    <div style="margin: 0px; padding: 0px;">
                        <p style="margin: 0px; padding: 0px; font-size: 13px;">
                            Dear {record.assignee_id.name},
                            <br/><br/>
                            You have been assigned to complete the Training Need: {record.name}
                            <br/><br/>
                            Details:
                            <ul>
                                <li>Department: {record.department_id.name}</li>
                                <li>Created by: {record.employee_id.name}</li>
                                <li>Registration Date: {record.registration_date}</li>
                                <li>Training Course Plan: {record.training_brochure_id.name}</li>
                            </ul>
                            <br/>
                            Please review and complete the required information.
                            <br/><br/>
                            Best regards,<br/>
                            {self.env.user.name}
                        </p>
                    </div>
                """
            }

            # Create and send email
            self.env['mail.mail'].create(mail_values).send()

        # Show success message with count of emails sent
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Notification emails sent to %s assignees') % len(self),
                'type': 'success',
                'sticky': False,
            }
        }


    #endregion
        
        
            
#region 1.3.2 Phê duyệt yêu cầu

    def _get_next_approver(self):
        pass


    def action_submit(self):
        """Submit the training need for approval"""
        for record in self:
            if record.state == 'draft' or record.state == 'rejected':
                record.write({
                    'state': 'submitted'
                })
                # Add to approval history
                self.env['hmv.training.need.approval'].create({
                    'training_need_id': record.id,
                    'employee_id': self.env.user.employee_id.id,
                    'status': 'approved',
                    'comment': 'Submitted for approval'
                })
                
        return True
    
    
    

    def action_manager_approve(self):
        """Manager approval"""
        for record in self:
            if record.state == 'submitted':
                return {
                    'name': _('Manager Approval'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'hmv.training.need.comment.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_action_type': 'approve',
                        'default_training_need_ids': [(6, 0, record.ids)],
                        'approval_type': 'manager',
                        'next_state': 'manager_approved'
                    }
                }
        return True

    def action_senior_manager_approve(self):
        """Senior Manager approval"""
        for record in self:
            if record.state == 'manager_approved':
                return {
                    'name': _('Senior Manager Approval'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'hmv.training.need.comment.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_action_type': 'approve',
                        'default_training_need_ids': [(6, 0, record.ids)],
                        'approval_type': 'senior_manager',
                        'next_state': 'senior_manager_approved'
                    }
                }
        return True

    def action_dgm_approve(self):
        """DGM approval"""
        for record in self:
            if record.state == 'senior_manager_approved':
                return {
                    'name': _('DGM Approval'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'hmv.training.need.comment.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_action_type': 'approve',
                        'default_training_need_ids': [(6, 0, record.ids)],
                        'approval_type': 'dgm',
                        'next_state': 'dgm_approved'
                    }
                }
        return True

    def action_gm_approve(self):
        """GM approval"""
        for record in self:
            if record.state == 'dgm_approved':
                return {
                    'name': _('GM Approval'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'hmv.training.need.comment.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_action_type': 'approve',
                        'default_training_need_ids': [(6, 0, record.ids)],
                        'approval_type': 'gm',
                        'next_state': 'gm_approved'
                    }
                }
        return True

    def action_officer_approve(self):
        """Officer approval"""
        for record in self:
            if record.state == 'gm_approved':
                return {
                    'name': _('Officer Approval'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'hmv.training.need.comment.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_action_type': 'approve',
                        'default_training_need_ids': [(6, 0, record.ids)],
                        'approval_type': 'officer',
                        'next_state': 'officer_approved'
                    }
                }
        return True

    def action_hr_manager_approve(self):
        """HR Manager approval"""
        for record in self:
            if record.state == 'officer_approved':
                return {
                    'name': _('HR Manager Approval'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'hmv.training.need.comment.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_action_type': 'approve',
                        'default_training_need_ids': [(6, 0, record.ids)],
                        'approval_type': 'hr_manager',
                        'next_state': 'completed'
                    }
                }
        return True
    


    # def action_reject(self):
    #     self.ensure_one()
    #     if self.state in ['completed','draft']:
    #         raise UserError(_("You cannot reject a completed/draft training need."))
            
    #     return {
    #         'name': _('Reject Training Need'),
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'hmv.training.need.comment.wizard',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {
    #             'default_action_type': 'refuse',
    #             'default_training_need_ids': [(6, 0, self.ids)],
    #         }
    #     }
        
        
    def action_reject(self):
        self.ensure_one()
        if self.state in ['completed','draft']:
            raise UserError(_("You cannot reject a completed/draft training need."))
            
        return {
            'name': _('Reject Training Need'),
            'type': 'ir.actions.act_window',
            'res_model': 'hmv.training.need.comment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_action_type': 'rejected',
                'default_training_need_ids': [(6, 0, self.ids)],
                'default_approval_status': 'rejected',  # Add this line to set default approval status
            }
        }
            
#endregion