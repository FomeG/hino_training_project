from Tools.scripts.dutree import store
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ApplicationForATC(models.Model):
    _name = 'application'
    _description = 'Application for Attending Training Course'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # remain_slots chua tinh, dynamic approval flow

    # Header
    name = fields.Char(string='Application No.', required=True, readonly=True, default=lambda self: _('New'),
                       help='Document number with format BS/YYYY/NNNN')
    x_applicant_id = fields.Many2one('hr.employee', string='Name of Applicant')
    x_department_id = fields.Many2one('hr.department', string='Department', related='x_applicant_id.department_id',
                                      store=True)
    x_position_id = fields.Many2one('hr.job', string='Position', related='x_applicant_id.job_id', store=True)
    x_request_date = fields.Date(string='Request Date', default=fields.Date.today, store=True)

    # Training course info
    x_course_title = fields.Many2one('hmv.training.courses', string='Course Title')
    x_start_date = fields.Date(string='Start Date', related='x_course_title.start_date', store=True)
    x_end_date = fields.Date(string='End Date', related='x_course_title.end_date', store=True)
    x_vendor_id = fields.Many2one('res.partner', string='Vendor', related='x_course_title.vendor_id')
    x_staff_id = fields.Many2many('hr.employee', string='P.I.C Staff/Dept', related='x_course_title.employee_id')
    x_slots = fields.Integer(string='Number of Slots', related='x_course_title.slot', store=True)
    x_remaining_slots = fields.Integer(string='Remaining Slots', compute='_compute_remaining_slots')
    x_training_content = fields.Text(string='Training Content', related='x_course_title.training_content')

    x_purpose_training = fields.Char(string='Purpose of attending training course')
    x_start_date_confirm = fields.Date(string='Start date of confirmation')
    x_end_date_confirm = fields.Date(string='End date of confirmation')
    x_department_apply_id = fields.Many2one('hr.department', string='Apply for department')
    x_training_plan_id = fields.Char(string='Training Plan')  # WHERE???
    x_training_method = fields.Many2one('hmv.list.value.line', string='Training Method',
                                        related='x_course_title.training_method_id')

    x_approval_status = fields.Selection([
        ('draft', 'Draft'),
        # ('editing', 'Editing'),
        # ('saved', 'Saved'),
        ('wait', 'Waiting to approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused')],
        string='Status', default='draft', readonly=True, tracking=True)

    x_course_count = fields.Integer(compute='_compute_course_count')
    x_is_form_readonly = fields.Boolean(string='Is Form Read Only?', compute='_compute_is_form_readonly')
    x_approval_history_ids = fields.One2many('approval.history', 'x_application_ids', string='Approval')
    x_is_all_approved = fields.Boolean(string='Is All Approved?', compute='_compute_is_all_approved')
    x_is_editable = fields.Boolean(string='Is Editable?', compute='_compute_is_editable')
    x_is_printable = fields.Boolean(string='Is Printable?', compute='_compute_is_printable')

    # Compute
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

    @api.depends('x_approval_status')
    def _compute_is_form_readonly(self):
        if self.x_approval_status in ('wait', 'approved', 'refused'):
            self.x_is_form_readonly = True
        else:
            self.x_is_form_readonly = False

    @api.depends('x_approval_history_ids.x_approval_status', 'x_approval_status')
    def _compute_is_printable(self):
        for record in self:
            if record.x_approval_status == 'approved' and record.x_is_all_approved:
                record.x_is_printable = True
            else:
                record.x_is_printable = False

    @api.depends('x_approval_history_ids.x_approval_status', 'x_approval_status')
    def _compute_is_editable(self):
        for record in self:
            if record.x_approval_status == 'refused' and record.x_is_all_approved == False:
                record.x_is_editable = True
            else:
                record.x_is_editable = False

    @api.depends('x_approval_history_ids.x_approval_status')
    def _compute_is_all_approved(self):
        for record in self:
            if record.x_approval_history_ids:
                record.x_is_all_approved = all(
                    history.x_approval_status == 'approved' for history in record.x_approval_history_ids
                )
            else:
                record.x_is_all_approved = False
        if self.x_is_all_approved:
            self.x_approval_status = 'approved'
            # Send notify for applicant
            '''......................'''

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
        self._create_approval_history()
        return True

    def action_button_edit(self):
        self.x_approval_history_ids.unlink()
        self.x_approval_status = 'draft'
        return True

    def action_button_save(self):
        self.x_approval_status = 'draft'
        return True

    # Button
    def action_button_approve(self):
        self._update_current_employee_approval_status('approved')
        self._compute_is_all_approved()
        return True

    def action_button_refuse(self):
        self._update_current_employee_approval_status('refused')
        # Send notify for applicant
        # self.x_applicant_id.message_post(body=f'Your application for attending training course has been refused.')
        return True

    # For TESTING
    def action_button_set_waiting(self):
        self.x_approval_status = 'draft'
        return True

    # Create Override
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq = self.env['ir.sequence'].next_by_code('application.sequence') or '0001'
            vals['name'] = f'{seq}'
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

    # Approval Workflow
    @staticmethod
    def _get_approval_flow():
        return ["Manager", "Senior Manager", "DGM", "GM", "Officer", "HR Manager"]

    def _get_manager(self):
        approval_flow = self._get_approval_flow()
        managers = []

        current_manager = self.x_applicant_id.parent_id
        # Find the next matching manager in the approval flow
        while current_manager:
            job_name = current_manager.job_id.name
            if job_name in approval_flow:
                managers.append(current_manager)

            current_manager = current_manager.parent_id

        return managers

    def _create_approval_history(self):
        """Creates an approval history record when an application is registered."""
        approval_history_model = self.env['approval.history']

        managers = self._get_manager()
        if not managers:
            raise ValidationError(_("No approval managers found for this position."))

        # Create an approval history record for each manager
        for manager in managers:
            approval_history_model.create({
                'x_application_ids': self.id,
                'x_approval_employee_id': manager.id,
                'x_approval_status': 'wait',
            })

    def _get_current_employee(self):
        """Get the current employee based on the user's employee_id"""
        current_employee = self.env.user.employee_id
        if not current_employee:
            raise ValidationError(_("No Employee found for the current user."))
        return current_employee

    def _update_current_employee_approval_status(self, new_status):
        """Update the approval status for the current employee"""
        current_employee = self._get_current_employee()

        # Find the correct line in the approval history
        approval_line = self.x_approval_history_ids.filtered(
            lambda line: line.x_approval_employee_id.id == current_employee.id
        )
        if not approval_line:
            raise ValidationError(_("You are not authorized to approve/refuse this application."))

        approval_line.write({'x_approval_status': new_status})


# Tab Approval History
class ApplicationApprovalHistory(models.Model):
    _name = 'approval.history'
    _description = 'Application Approval History'

    x_application_ids = fields.Many2one('application', string='Application ID')
    x_approval_employee_id = fields.Many2one('hr.employee', string='Approved by')
    x_approval_job_id = fields.Many2one('hr.job', string='Position', related='x_approval_employee_id.job_id')
    x_approval_department_id = fields.Many2one('hr.department', string='Department',
                                               related='x_approval_employee_id.department_id')
    x_approval_status = fields.Selection([
        ('wait', 'Waiting to approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused')],
        string='Status', default='wait', readonly=True, tracking=True)
    x_approval_comment = fields.Text(string='Comment')
    x_is_approval_readonly = fields.Boolean(string='Is Approval Read Only?', compute='_compute_is_approval_readonly')

    @api.depends('x_approval_status')
    def _compute_is_approval_readonly(self):
        for record in self:
            if record.x_approval_status in ('approved', 'refused'):
                record.x_is_approval_readonly = True
            else:
                record.x_is_approval_readonly = False
