from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class TabApprovalTraining(models.Model):
    _name = 'hmv.tab.approval.training'
    _description = 'Training Plan Approval'

    comment = fields.Char(string='Comment')

    training_plan_id = fields.Many2one('hmv.training.plan', string='Training Plan', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='Approver')
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
        ('waiting', 'Waiting'),
        ('approved', 'Approved'),
        ('refused', 'Refused')
    ], string='Status', default='waiting')

    def action_approve(self):
        return {
            'name': 'Approval Confirmation',
            'type': 'ir.actions.act_window',
            'res_model': 'hmv.training.plan.comment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_training_plan_id': self.training_plan_id.id,
                'default_action_type': 'approve'
            }
        }

    def action_refuse(self):
        return {
            'name': 'Refusal Confirmation',
            'type': 'ir.actions.act_window',
            'res_model': 'hmv.training.plan.comment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_training_plan_id': self.training_plan_id.id,
                'default_action_type': 'refuse'
            }
        }
