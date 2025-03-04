from odoo import models, fields, api, _

class TrainingNeedCommentWizard(models.TransientModel):
    _name = 'hmv.training.need.comment.wizard'
    _description = 'Training Need Comment Wizard'

    comment = fields.Text(string='Comment', required=True)
    action_type = fields.Selection([
        ('approve', 'Approve'),
        ('rejected', 'Rejected')
    ], string='Action Type', required=True)
    
    approval_status = fields.Selection([
        ('manager_approved', 'Manager Approved'),
        ('senior_manager_approved', 'Senior Manager Approved'), 
        ('dgm_approved', 'DGM Approved'),
        ('gm_approved', 'GM Approved'),
        ('officer_approved', 'Officer Approved'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected')
    ], string='Approval Status', required=True)
    
    training_need_ids = fields.Many2many('hmv.training.need', string='Training Needs')

    @api.model 
    def default_get(self, fields):
        res = super(TrainingNeedCommentWizard, self).default_get(fields)
        
        # Map approval types to statuses
        approval_type = self.env.context.get('approval_type')
        status_mapping = {
            'manager': 'manager_approved',
            'senior_manager': 'senior_manager_approved',
            'dgm': 'dgm_approved',
            'gm': 'gm_approved',
            'officer': 'officer_approved',
            'hr_manager': 'completed'
        }
        
        if approval_type:
            res['approval_status'] = status_mapping.get(approval_type)
            
        return res

    def action_confirm(self):
        self.ensure_one()
        if not self.comment:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Warning'),
                    'message': _('Please enter a comment'),
                    'type': 'warning',
                    'sticky': False,
                }
            }
            
        active_id = self.env.context.get('active_id')
        training_need = self.env['hmv.training.need'].browse(active_id)
        
        if training_need:
            # Create approval history record
            self.env['hmv.training.need.approval'].create({
                'training_need_id': training_need.id,
                'employee_id': self.env.user.employee_id.id,
                'status': 'approved' if self.action_type == 'approve' else 'rejected',
                'comment': self.comment,
            })
            
            # Update training need state based on approval status
            if self.action_type == 'approve':
                training_need.write({'state': self.approval_status})
            elif self.action_type == 'rejected':
                # When rejecting, set approval_status to 'rejected' explicitly
                self.approval_status = 'rejected'
                training_need.write({'state': 'rejected'})
            
        return {'type': 'ir.actions.act_window_close'}




    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}