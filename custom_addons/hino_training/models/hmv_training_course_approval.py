from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TrainingCourseApproval(models.Model):
    _name = 'hmv.training.course.approval'
    _description = 'Training Course Approval History'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'
    _order = 'sequence'

    training_course_id = fields.Many2one('hmv.training.courses', string='Training Course', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    employee_id = fields.Many2one('hr.employee', string='Approver', required=True, tracking=True)
    job_id = fields.Many2one(related='employee_id.job_id', string='Position', store=True, readonly=True, tracking=True)
    department_id = fields.Many2one(related='employee_id.department_id', string='Department', store=True, readonly=True,
                                    tracking=True)
    status = fields.Selection([
        ('waiting', 'Waiting to approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused')
    ], string='Status', default='waiting', tracking=True)
    approval_level = fields.Selection([
        ('staff', 'Staff'),
        ('hr_manager', 'HR Manager'),
        ('fd', 'Finance Director'),
        ('gd', 'General Director')
    ], string='Approval Level', required=True, tracking=True)
    comment = fields.Text(string='Comment', tracking=True)
    date = fields.Datetime(string='Action Date', tracking=True)

    @api.model
    def create(self, vals):
        vals['date'] = fields.Datetime.now()
        return super().create(vals)

    def write(self, vals):
        if 'status' in vals:
            vals['date'] = fields.Datetime.now()
        return super().write(vals)

