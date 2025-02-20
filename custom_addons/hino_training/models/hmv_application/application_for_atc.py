from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ApplicationForATC(models.Model):
    _name = 'application'
    _description = 'Application for Attending Training Course'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Header
    name = fields.Char(string='Application No.', required=True, readonly=True, default=lambda self: _('New'),
                       help='Document number with format BS/YYYY/NNNN')
    x_applicant_id = fields.Many2one('hr.employee', string='Name of Applicant')
    x_department_id = fields.Many2one('hr.department', string='Department')
    x_position_id = fields.Char(string='Position', help='Input your position')
    x_request_date = fields.Date(string='Request Date',
                                     help='The Request Date CAN NOT be later than the Start Date')

    # Training course info
    x_course_title = fields.Many2one('hmv.training.courses', string='Course Title')
    x_start_date = fields.Date(string='Start Date', related='x_course_title.start_date', store=True)
    x_end_date = fields.Date(string='End Date', related='x_course_title.end_date', store=True)
    x_vendor_id = fields.Many2one(string='Vendor', related='x_course_title.vendor_id')
    x_staff_id = fields.Many2one(string='P.I.C Staff/Dept', related='x_course_title.employee_hr_id')
    x_slots = fields.Integer(string='Number of Slots', related='x_course_title.slot', store=True)
    x_remaining_slots = fields.Integer(string='Remaining Slots', compute='_compute_remaining_slots')
    x_training_content = fields.Text(string='Training Content', related='x_course_title.training_content')

    x_purpose_training = fields.Char(string='Purpose of attending training course')
    x_start_date_confirm = fields.Date(string='Start date of confirmation')
    x_end_date_confirm = fields.Date(string='End date of confirmation')
    x_department_apply_id = fields.Many2one('hr.department', string='Apply for department')
    x_training_plan_id = fields.Char(string='Training Plan')
    x_training_method = fields.Char(string='Training Method') # ???

    # Tab Approval history
    x_approval_employee_id = fields.Many2one('hr.employee', string='Approved by')
    x_approval_job_id = fields.Many2one('hr.job', string='Position', related='x_approval_employee_id.job_id')
    x_approval_department_id = fields.Many2one('hr.department', string='Department', related='x_approval_employee_id.department_id')
    x_approval_status = fields.Selection([
        ('draft', 'Draft'),
        # ('editing', 'Editing'),
        # ('saved', 'Saved'),
        ('wait', 'Waiting to approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused')],
        string='Status', default='draft', readonly=True)
    x_approval_comment = fields.Text(string='Comment')

    x_course_count = fields.Integer(compute='_compute_course_count')

    def _compute_course_count(self):
        for record in self:
            record.x_course_count = self.env['hmv.training.courses'].search_count(
                [('participant_ids', 'in', record.x_applicant_id.id)])

    def _compute_remaining_slots(self):
        for record in self:
            if record.x_course_title:
                record.x_remaining_slots = record.x_slots - len(record.x_course_title.participant_ids)
            else:
                record.x_remaining_slots = 0

    # Smart Button
    def action_button_open_training_course(self):
        if not self.x_course_title:
            raise ValidationError(_("No training course selected!"))
        return {
            'name': 'Open Training Course',
            'type': 'ir.actions.act_window',
            'res_model': 'hmv.training.courses',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.x_course_title.id,
            'target': 'new',
        }

    def action_button_print(self):
        return self.env.ref('hino_training.report_application_for_atc').report_action(self)

    def action_button_register(self):
        self.x_approval_status = 'wait'

    def action_button_edit(self):
        self.x_approval_status = 'draft'

    def action_button_save(self):
        self.x_approval_status = 'draft'

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
            if record.x_request_date and record.x_start_date:  # Ensure both are set
                if record.x_request_date > record.x_start_date:
                    raise ValidationError(_('The Request Date cannot be later than the Start Date.'))

    @api.constrains('x_slots')
    def _check_slots(self):
        for record in self:
            if record.x_slots < 1:
                raise ValidationError(_('Number of slots must be at least 1.'))

    @api.constrains('x_start_date', 'x_end_date')
    def _check_dates(self):
        for record in self:
            if record.x_start_date and record.x_end_date:  # Ensure both are set
                if record.x_start_date > record.x_end_date:
                    raise ValidationError(_('The Start Date must be before the End Date.'))
