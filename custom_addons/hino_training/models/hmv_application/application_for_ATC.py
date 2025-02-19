from odoo import api, fields, models, _


class ApplicationForATC(models.Model):
    _name = 'application'
    _description = 'Application for Attending Training Course'

    # Header
    name = fields.Char('BS', required=True, readonly=True, default=lambda self: _('New'),
                       help='Document number with format BS/YYYY/NNNN')
    x_applicant_id = fields.Many2one('hr.employee', string='Name of Applicant')
    x_department_id = fields.Many2one('hr.department', string='Department')
    x_position_id = fields.Char(string='Position', help='Input your position')
    x_date = fields.Datetime(string='Request Date', help='The Request Date CAN NOT be later than the Start Date')

    # Training course info
    x_course_title = fields.Char(string='Course Title')
    x_start_date = fields.Datetime(string='Start Date')
    x_end_date = fields.Datetime(string='End Date')
    x_vendor_id = fields.Char(string='Vendor')
    x_staff_id = fields.Char(string='P.I.C Staff/Dept')
    x_slots = fields.Integer(string='Number of Slots')
    x_remaining_slots = fields.Integer(string='Remaining Slots')
    x_training_content = fields.Text(string='Training Content')

    x_purpose_training = fields.Char(string='Purpose of attending training course')
    x_start_date_confirm = fields.Datetime(string='Start date of confirmation')
    x_end_date_confirm = fields.Datetime(string='End date of confirmation')
    x_department_apply_id = fields.Many2one('hr.department', string='Apply for department')
    x_training_plan_id = fields.Char(string='Training Plan')
    x_training_method = fields.Char(string='Training Method')

    def action_button_edit(self):
        return

    def action_button_save(self):
        return

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('application.sequence') or '0001'
            vals['name'] = f'BS{seq}'
        return super(ApplicationForATC, self).create(vals)
