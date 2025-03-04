from odoo import models, fields, _
from odoo.exceptions import ValidationError


class TrainingApprovalWizard(models.TransientModel):
    _name = 'hmv.training.approval.wizard'
    _description = 'Training Approval Comment Wizard'

    approval_id = fields.Many2one('hmv.training.course.approval', string='Approval')
    training_course_id = fields.Many2one('hmv.training.courses', string='Training Course')
    action_type = fields.Selection([
        ('approved', 'Approve'),
        ('refused', 'Refuse')
    ], string='Action')
    approval_level = fields.Selection([
        ('staff', 'Staff'),
        ('hr_manager', 'HR Manager'),
        ('fd', 'Finance Director'),
        ('gd', 'General Director')
    ], string='Approval Level')
    comment = fields.Text(string='Comment')

    def action_confirm(self):
        """Confirm the approval or rejection"""
        self.ensure_one()

        if not self.approval_id:
            raise ValidationError(_("No approval record found."))

        # Update the approval record
        self.approval_id.write({
            'status': self.action_type,
            'comment': self.comment,
            'date': fields.Datetime.now()
        })

        training_course = self.approval_id.training_course_id

        # Process based on action type
        if self.action_type == 'approved':
            current_level = self.approval_level

            # Define the next status based on current level
            next_status_map = {
                'staff': 'hr_approval',
                'hr_manager': 'fd_approval',
                'fd': 'gd_approval',
                'gd': 'active'
            }

            next_status = next_status_map.get(current_level)
            if next_status:
                training_course.write({'status': next_status})

        elif self.action_type == 'refused':
            # Reject the course, return to draft
            training_course.write({'status': 'draft'})

        return {'type': 'ir.actions.act_window_close'}