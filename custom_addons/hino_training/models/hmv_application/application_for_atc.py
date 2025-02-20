from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ApplicationForATC(models.Model):
    _name = 'application'
    _description = 'Application for Attending Training Course'

    # Header
    name = fields.Char(string='Application No.', required=True, readonly=True, default=lambda self: _('New'),
                       help='Document number with format BS/YYYY/NNNN')
    x_applicant_id = fields.Many2one('hr.employee', string='Name of Applicant')
    x_department_id = fields.Many2one('hr.department', string='Department')
    x_position_id = fields.Char(string='Position', help='Input your position')
    x_request_date = fields.Datetime(string='Request Date',
                                     help='The Request Date CAN NOT be later than the Start Date')

    # Training course info
    x_course_title = fields.Many2one('hmv.training.courses', string='Course Title')
    x_start_date = fields.Date(string='Start Date', related='x_course_title.start_date')
    x_end_date = fields.Date(string='End Date', related='x_course_title.end_date')
    x_vendor_id = fields.Many2one(string='Vendor', related='x_course_title.vendor_id')
    x_staff_id = fields.Char(string='P.I.C Staff/Dept')
    x_slots = fields.Integer(string='Number of Slots', related='x_course_title.slot')
    x_remaining_slots = fields.Integer(string='Remaining Slots')
    x_training_content = fields.Text(string='Training Content')

    x_purpose_training = fields.Char(string='Purpose of attending training course')
    x_start_date_confirm = fields.Datetime(string='Start date of confirmation')
    x_end_date_confirm = fields.Datetime(string='End date of confirmation')
    x_department_apply_id = fields.Many2one('hr.department', string='Apply for department')
    x_training_plan_id = fields.Char(string='Training Plan')
    x_training_method = fields.Char(string='Training Method')

    # Tab Approval history
    x_approval_employee_id = fields.Many2one('hr.employee', string='Approved by')
    x_approval_job_id = fields.Many2one('hr.job', string='Position', related='x_approval_employee_id.job_id')
    x_approval_department_id = fields.Many2one('hr.department', string='Department', related='x_approval_employee_id.department_id')
    x_approval_status = fields.Selection([
        ('draft', 'Draft'),
        ('wait', 'Waiting to approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused')],
        string='Status', default='draft', readonly=True)
    x_approval_comment = fields.Text(string='Comment')

    # Smart Button
    def action_button_register(self):
        self.x_approval_status = 'wait'

    def action_button_edit(self):
        return

    def action_button_save(self):
        return

    # Button
    def action_button_approve(self):
        self.x_approval_status = 'approved'

    def action_button_refuse(self):
        self.x_approval_status = 'refused'
        # Send notify for applicant
        # self.x_applicant_id.message_post(body=f'Your application for attending training course has been refused.')

    # For TESTING
    def action_button_set_waiting(self):
        self.x_approval_status = 'draft'

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('application.sequence') or '0001'
            vals['name'] = f'BS{seq}'
        return super(ApplicationForATC, self).create(vals)

    # For VALIDATING
    @api.constrains('x_request_date', 'x_start_date')
    def _check_request_date(self):
        for record in self:
            if record.x_request_date and record.x_start_date and record.x_request_date > record.x_start_date:
                raise ValidationError(_('The Request Date cannot be later than the Start Date.'))

    @api.constrains('x_slots')
    def _check_slots(self):
        for record in self:
            if record.x_slots < 1:
                raise ValidationError(_('Number of slots must be at least 1.'))

    @api.constrains('x_start_date', 'x_end_date')
    def _check_dates(self):
        for record in self:
            if record.x_start_date and record.x_end_date and record.x_start_date > record.x_end_date:
                raise ValidationError(_('The Start Date must be before the End Date.'))
