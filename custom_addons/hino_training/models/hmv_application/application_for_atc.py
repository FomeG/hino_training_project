from Tools.scripts.dutree import store
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


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
    x_remaining_slots = fields.Integer(string='Remaining Slots', related='x_course_title.remaining_slots', store=True)
    x_training_content = fields.Text(string='Training Content', related='x_course_title.training_content')

    x_purpose_training = fields.Char(string='Purpose of attending training course')
    x_start_date_confirm = fields.Date(string='Start date of confirmation')
    x_end_date_confirm = fields.Date(string='End date of confirmation')
    x_department_apply_id = fields.Many2one('hr.department', string='Apply for department')
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

    # Use for change readonly, ...
    x_course_count = fields.Integer(compute='_compute_course_count')
    x_is_form_readonly = fields.Boolean(string='Is Form Read Only?', compute='_compute_is_form_readonly')
    x_approval_history_ids = fields.One2many('approval.history', 'x_application_ids', string='Approval')
    x_is_all_approved = fields.Boolean(string='Is All Approved?', compute='_compute_is_all_approved')
    x_is_editable = fields.Boolean(string='Is Editable?', compute='_compute_is_editable')
    x_is_printable = fields.Boolean(string='Is Printable?', compute='_compute_is_printable')

    # Additional fields
    x_applicant_email = fields.Char(string='Applicant Email', compute='_compute_applicant_email', store=True)
    computed_domain = fields.Char(string='Computed Domain', compute='_compute_computed_domain')

    @api.onchange('x_course_title')
    def _compute_computed_domain(self):
        if self.env.user.department_id.name == 'HR':
            self.computed_domain = [('status', '=', 'active')]
        else:
            self.computed_domain = [('status', '=', 'active'), ('course_type', '=', 'public')]

    # Compute
    def _compute_course_count(self):
        for record in self:
            record.x_course_count = self.env['hmv.training.participant'].search_count(
                [('employee_id', '=', record.x_applicant_id.id)])

    # def _compute_remaining_slots(self):
    #     for record in self:
    #         if record.x_course_title:
    #             record.x_remaining_slots = record.x_slots - len(record.x_course_title.participant_ids)
    #         else:
    #             record.x_remaining_slots = 0

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

    @api.onchange('x_applicant_id')
    def _compute_applicant_email(self):
        for record in self:
            if record.x_applicant_id:
                record.x_applicant_email = record.x_applicant_id.work_email
            else:
                record.x_applicant_email = ''

    # Create applicant in course
    def _prepare_data_for_participant(self):
        """ Prepare data for participants """
        self.ensure_one()
        data = {
            'course_id': self.x_course_title.id,
            'employee_id': self.x_applicant_id.id,
        }
        return data

    def _create_participant(self):
        """ Create participant """
        participant_data = self._prepare_data_for_participant()
        print(participant_data)
        existing_participant = self.env['hmv.training.participant'].search([
            ('course_id', '=', participant_data['course_id']),
            ('employee_id', '=', participant_data['employee_id']),
        ], limit=1)

        if not existing_participant:
            self.env['hmv.training.participant'].create(participant_data)

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
            print('Creating Participant')
            print(self.x_is_all_approved)
            self._create_participant()

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

    def send_application_confirmation_email(self):
        for record in self:
            if not record.x_applicant_email:
                raise UserError("Applicant Email is missing.")

            mail_values = {
                'subject': f'Confirmation: Application for Attending {record.x_course_title.course_title}',
                'email_from': 'your_configured_email@gmail.com',
                'email_to': record.x_applicant_email,
                'body_html': f"""
                    <div style="font-family: Arial, sans-serif; color: #333;">
                        <p style="font-size: 16px;">Dear <strong>{record.x_applicant_id.name}</strong>,</p>

                        <p>Thank you for applying to our training program! We have received your application, and we are excited to have you join us.</p>

                        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;" />

                        <h3 style="color: #007BFF;">Application Details</h3>
                        <table style="width: 100%; border-collapse: collapse; text-align: left;">
                            <tr>
                                <th style="padding: 10px; border: 1px solid #ddd; background-color: #f2f2f2; width: 40%;">Fields</th>
                                <th style="padding: 10px; border: 1px solid #ddd; background-color: #f2f2f2; width: 60%;">Details</th>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Application Code:</strong></td>
                                <td style="padding: 10px; border: 1px solid #ddd;">{record.name}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Course:</strong></td>
                                <td style="padding: 10px; border: 1px solid #ddd;">{record.x_course_title.course_title}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Start Date:</strong></td>
                                <td style="padding: 10px; border: 1px solid #ddd;">{record.x_start_date}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border: 1px solid #ddd;"><strong>End Date:</strong></td>
                                <td style="padding: 10px; border: 1px solid #ddd;">{record.x_end_date}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Vendor:</strong></td>
                                <td style="padding: 10px; border: 1px solid #ddd;">{record.x_vendor_id.name}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Apply for Department:</strong></td>
                                <td style="padding: 10px; border: 1px solid #ddd;">{record.x_department_apply_id.name}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Training Content:</strong></td>
                                <td style="padding: 10px; border: 1px solid #ddd;">{record.x_training_content}</td>
                            </tr>
                        </table>

                        <h3 style="color: #007BFF; margin-top: 20px;">Confirmation Details</h3>
                        <table style="width: 100%; border-collapse: collapse; text-align: left;">
                            <tr>
                                <th style="padding: 10px; border: 1px solid #ddd; background-color: #f2f2f2; width: 40%;">Fields</th>
                                <th style="padding: 10px; border: 1px solid #ddd; background-color: #f2f2f2; width: 60%;">Details</th>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Confirmed Start Date:</strong></td>
                                <td style="padding: 10px; border: 1px solid #ddd;">{record.x_start_date_confirm}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border: 1px solid #ddd;"><strong>Confirmed End Date:</strong></td>
                                <td style="padding: 10px; border: 1px solid #ddd;">{record.x_end_date_confirm}</td>
                            </tr>
                        </table>

                        <p style="margin-top: 20px;">If you have any questions, feel free to contact us.</p>

                        <p style="font-size: 16px; margin-top: 20px;">Best regards,</p>
                        <p style="font-size: 16px;"><strong>The HR Team</strong></p>
                    </div>
                """
            }

            self.env['mail.mail'].create(mail_values).send()

        return True

    # Button
    def action_button_approve(self):
        self._update_current_employee_approval_status('approved')
        self._compute_is_all_approved()
        self._validate_workflow()
        return {
            'name': 'Approval Comment',
            'type': 'ir.actions.act_window',
            'res_model': 'approval.history',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_button_refuse(self):
        self._update_current_employee_approval_status('refused')
        # Send notify for applicant
        # self.x_applicant_id.message_post(body=f'Your application for attending training course has been refused.')
        return {
            'name': 'Rejection Comment',
            'type': 'ir.actions.act_window',
            'res_model': 'approval.history',
            'view_mode': 'form',
            'target': 'new',
        }

    # For TESTING
    def action_button_set_waiting(self):
        self.x_approval_status = 'draft'
        self.x_approval_history_ids.unlink()
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

    @api.constrains('x_remaining_slots')
    def _check_remaining_slots(self):
        for record in self:
            if record.x_remaining_slots < 0:
                raise ValidationError(_('The Remaining Slots cannot be less than 0.'))

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

    def _validate_workflow(self):
        """Validates the approval workflow for the application."""
        # Get the current employee and the approval flow
        current_employee = self._get_current_employee()
        approval_flow = self._get_approval_flow()

        #  Get current employee's job name
        current_job = current_employee.job_id.name

        # Find the index of the current employee's job in the approval flow
        current_index = -1
        for index in range(len(approval_flow)):
            if approval_flow[index] == current_job:
                current_index = index
                break
        if current_index == -1:
            raise ValidationError(_('Current employee job not found in the approval flow.'))

        for i in range(current_index):
            role_to_check = approval_flow[i]
            found = False

            for record in self.x_approval_history_ids:
                if record.x_approval_employee_id.job_id.name == role_to_check:
                    found = True
                    if record.x_approval_status != 'approved':
                        raise ValidationError(_('The previous approval for role "%s" is not approved.') % role_to_check)
                    break

    def _create_approval_history(self):
        """Creates an approval history record when an application is registered."""
        approval_history_model = self.env['approval.history']

        managers = self._get_manager()
        if not managers:
            managers.append(self.x_applicant_id)

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
    x_approval_comment = fields.Text(string='Comment', default='')
    x_is_approval_readonly = fields.Boolean(string='Is Approval Read Only?', compute='_compute_is_approval_readonly')

    def action_submit_comment(self):
        active_id = self.env.context.get('active_id')
        application = self.env['application'].browse(active_id)
        if application and application.x_approval_history_ids:
            # Lọc ra bản ghi approval history có employee_id trùng với employee của current user
            target_history = application.x_approval_history_ids.filtered(
                lambda rec: rec.x_approval_employee_id.id == self.env.user.employee_id.id
            )
            if target_history:
                target_history.write({'x_approval_comment': self.x_approval_comment})
        return {'type': 'ir.actions.act_window_close'}

    @api.depends('x_approval_status')
    def _compute_is_approval_readonly(self):
        for record in self:
            if record.x_approval_status in ('approved', 'refused'):
                record.x_is_approval_readonly = True
            else:
                record.x_is_approval_readonly = False
