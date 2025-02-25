from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date


class TrainingCourses(models.Model):
    _name = 'hmv.training.courses'
    _description = 'Training Courses'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'course_title'


    course_title = fields.Char(string='Course Title', required=True, tracking=True)
    start_date = fields.Date(string='Start date', required=True, tracking=True)
    end_date = fields.Date(string='End date', required=True, tracking=True)
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True, tracking=True,
                                domain=[('is_company', '=', True)])
    purchase_order_id = fields.Many2one('purchase.order', string='Link PO', tracking=True)
    employee_id = fields.Many2many('hr.employee', string='P.I.C Staff/Dept', required=True,
                                   tracking=True)
    slot = fields.Integer(string='Slots', required=True, tracking=True)
    training_content = fields.Text(string='Training content', required=True, tracking=True)
    file_attach = fields.Binary(string='File Attach', attachment=True)
    confirmation_start_date = fields.Date(string='Start date of confirmation', required=True, tracking=True)
    confirmation_end_date = fields.Date(string='End date of confirmation', required=True, tracking=True)
    department_id = fields.Many2one('hr.department', string='Apply for department', required=True, tracking=True)
    training_method_id = fields.Many2one('hmv.list.value.line', string='Training Method', required=True,
                                         tracking=True, domain=[('code', '=', 'TRAINING_METHOD')])
    year = fields.Date(string='Year', required=True, tracking=True)
    training_brochure_id = fields.Many2one('hmv.training.brochure.line', string='Training brochure',
                                           required=True, tracking=True)
    
    

    location_id = fields.Many2one('res.country.state', string='Location', required=True, tracking=True)
    employee_hr_id = fields.Many2one('hr.employee', string='Prepared', tracking=True,)
    deptcombine = fields.Text(string='DeptCombine', tracking=True)
    description = fields.Text(string='Description', required=True, tracking=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('in_progress', 'In progress'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ], string='Status', required=True, default='draft', tracking=True)
    course_type = fields.Selection([
        ('public', 'Public'),
        ('in_house', 'In-house')
    ], string='Course Type', required=True, tracking=True) # lấy từ training need
    estimate_fee = fields.Monetary(string='Actual Fee', required=True, tracking=True) # lấy từ training need
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    audience_ids = fields.Many2one('hmv.list.value.line', string='Audience', required=True,
                                   tracking=True, domain=[('code', '=', 'TR_LEVEL')])
    participant_ids = fields.One2many('hmv.training.participant', 'course_id', string='Participants')
    # New Approval Fields
    approval_employee_id = fields.Many2one('hr.employee', string='Approver', tracking=True)
    approval_job_id = fields.Many2one(related='approval_employee_id.job_id', string='Position',
                                      store=True, readonly=True, tracking=True)
    approval_department_id = fields.Many2one(related='approval_employee_id.department_id',
                                             string='Department', store=True, readonly=True, tracking=True)
    approval_status = fields.Selection([
        ('waiting', 'Waiting to approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused')
    ], string='Approval Status', default='waiting', tracking=True)
    approval_comment = fields.Text(string='Approval Comment', tracking=True)
    remaining_slots = fields.Integer(
        string='Remaining Slots',
        compute='_compute_remaining_slots',
        store=True,
        help='Number of available slots remaining in the course'
    )

    @api.depends('slot', 'participant_ids')
    def _compute_remaining_slots(self):
        for record in self:
            total_participants = len(record.participant_ids)
            record.remaining_slots = record.slot - total_participants

    def action_register_course(self):
        """Register for a course based on course type and user permissions"""
        # Check if course is in active state
        if self.status != 'active':
            raise ValidationError(_("Course registration is only available for active courses."))

        # Check if approval is completed
        if self.approval_status != 'approved':
            raise ValidationError(_("Course must be approved before registration."))

        # Check remaining slots
        if self.remaining_slots <= 0:
            raise ValidationError(_("No slots remaining in this course."))

        # Get current user's employee record
        current_employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)], limit=1)
        if not current_employee:
            raise ValidationError(_("You must be an employee to register for courses."))

        # Handle In-house courses
        if self.course_type == 'in_house':
            # Check if user is from HR department
            if not self.env.user.has_group('hr.group_hr_user'):
                raise ValidationError(
                    _("Only HR department members can register participants for in-house courses."))

        # Check if employee is already registered
        if self.participant_ids.filtered(lambda p: p.employee_id.id == current_employee.id):
            raise ValidationError(_("You are already registered for this course."))

        # Create participant record
        self.env['hmv.training.participant'].create({
            'course_id': self.id,
            'employee_id': current_employee.id,
            'status': 'waiting'
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Successfully registered for the course.'),
                'type': 'success',
                'sticky': False,
            }
        }
    @api.constrains('start_date', 'end_date', 'confirmation_start_date', 'confirmation_end_date')
    def _check_dates(self):
        for record in self:
            today = date.today()
            if record.start_date and record.start_date < today:
                raise ValidationError(_("Start date cannot be earlier than today."))
            if record.end_date and record.start_date and record.end_date < record.start_date:
                raise ValidationError(_("End date cannot be earlier than start date."))
            if record.confirmation_start_date and record.confirmation_start_date < today:
                raise ValidationError(_("Confirmation start date cannot be earlier than today."))
            if (record.confirmation_end_date and record.confirmation_start_date and
                    record.confirmation_end_date < record.confirmation_start_date):
                raise ValidationError(_("Confirmation end date cannot be earlier than confirmation start date."))

    @api.constrains('slot')
    def _check_slot(self):
        for record in self:
            if record.slot <= 0:
                raise ValidationError(_("Number of slots must be positive."))

    @api.onchange('vendor_id')
    def _onchange_vendor_id(self):
        if self.vendor_id:
            return {'domain': {'purchase_order_id': [('partner_id', '=', self.vendor_id.id)]}}

    @api.onchange('year')
    def _onchange_year(self):
        if self.year:
            return {'domain': {'training_brochure_id': [('year', '=', self.year)]}}

    # @api.onchange('training_brochure_id')
    # def _onchange_training_brochure_id(self):
    #     if self.training_brochure_id:
    #         self.course_type = self.training_brochure_id.course_type
    #         self.estimate_fee = self.training_brochure_id.estimate_fee

    def action_edit(self):
        if self.status not in ['draft', 'refused']:
            raise ValidationError(
                _("Training Courses can only be edited when in 'Draft' state or refused by approver."))
        return True

    def action_save(self):
        if self.status != 'draft':
            raise ValidationError(_("Training Courses can only be saved when in 'Draft' state."))
        return True

    def action_active(self):
        if self.status != 'draft':
            raise ValidationError(_("Only courses in 'Draft' state can be activated."))
        self.status = 'active'
        return True

    def action_start(self):
        if self.status != 'active':
            raise ValidationError(_("Only courses in 'Active' state can be started."))
        self.status = 'in_progress'
        return True

    def action_done(self):
        if self.status != 'in_progress':
            raise ValidationError(_("Only courses in 'In Progress' state can be marked as done."))
        self.status = 'done'
        return True

    def action_cancel(self):
        if self.status not in ['active', 'in_progress']:
            raise ValidationError(_("Only courses in 'Active' or 'In Progress' state can be cancelled."))
        self.status = 'cancel'
        return True

    def action_create(self):
        return True

    def send_confirmation_email(self):
        template = self.env.ref('hmv_training.email_template_training_confirmation')
        for participant in self.participant_ids.filtered(lambda p: p.status == 'waiting'):
            template.send_mail(participant.id, force_send=True)
        return True
