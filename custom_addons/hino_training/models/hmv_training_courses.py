from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError
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
    file_attach = fields.Many2many('ir.attachment', string='File Attach', attachment=True)
    confirmation_start_date = fields.Date(string='Start date of confirmation', required=True, tracking=True)
    confirmation_end_date = fields.Date(string='End date of confirmation', required=True, tracking=True)
    department_id = fields.Many2one('hr.department', string='Apply for department', required=True, tracking=True)
    training_method_id = fields.Many2one('hmv.list.value.line', string='Training Method',
                                         tracking=True, domain=[('code', '=', 'TRAINING_METHOD')])
    year = fields.Char(string='Year', compute='_compute_year', store=True)
    training_brochure_id = fields.Many2one('hmv.training.brochure.line', string='Training brochure',
                                           tracking=True)
    location_id = fields.Many2one('res.country.state', string='Location', required=True, tracking=True)
    employee_hr_id = fields.Many2one('hr.employee', string='Prepared', tracking=True)
    deptcombine = fields.Text(string='DeptCombine', tracking=True)
    description = fields.Text(string='Description', required=True, tracking=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('staff_approval', 'Staff Approval'),
        ('hr_approval', 'HR Manager Approval'),
        ('fd_approval', 'Finance Director Approval'),
        ('gd_approval', 'General Director Approval'),
        ('active', 'Active'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ], string='Status', required=True, default='draft', tracking=True)

    course_type = fields.Selection([
        ('public', 'Public'),
        ('in_house', 'In-house')
    ], string='Course Type', required=True, tracking=True)
    estimate_fee = fields.Monetary(string='Actual Fee', required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    audience_ids = fields.Many2one('hmv.list.value.line', string='Audience',
                                   tracking=True, domain=[('code', '=', 'TR_LEVEL')])
    participant_ids = fields.One2many('hmv.training.participant', 'course_id', string='Participants')

    # Approval Fields
    approval_ids = fields.One2many('hmv.training.course.approval', 'training_course_id',
                                   string='Approval History', tracking=True)
    current_approval_id = fields.Many2one('hmv.training.course.approval',
                                          string='Current Approval', compute='_compute_current_approval')
    remaining_slots = fields.Integer(
        string='Remaining Slots',
        compute='_compute_remaining_slots',
        store=True,
        help='Number of available slots remaining in the course'
    )
    current_approval_level = fields.Selection([
        ('staff', 'Staff'),
        ('hr_manager', 'HR Manager'),
        ('fd', 'Finance Director'),
        ('gd', 'General Director')
    ], string='Current Approval Level', compute='_compute_current_approval_level', store=True)

    @api.depends('start_date')
    def _compute_year(self):
        for record in self:
            if record.start_date:
                record.year = fields.Datetime.from_string(record.start_date).strftime('%Y')
            else:
                record.year = 0

    @api.depends('approval_ids.status', 'approval_ids.sequence')
    def _compute_current_approval_level(self):
        for record in self:
            pending_approvals = record.approval_ids.filtered(lambda a: a.status == 'waiting')
            if pending_approvals:
                first_pending = min(pending_approvals, key=lambda a: a.sequence)
                if first_pending.approval_level:
                    record.current_approval_level = first_pending.approval_level
                else:
                    record.current_approval_level = False
            else:
                record.current_approval_level = False

    @api.depends('slot', 'participant_ids.status')
    def _compute_remaining_slots(self):
        for record in self:
            agreed_participants = self.env['hmv.training.participant'].search_count([
                ('course_id', '=', record.id),
                ('status', '=', 'agreed')
            ])
            record.remaining_slots = record.slot - agreed_participants

    def action_register_course(self):
        """Register for a course based on course type and user permissions"""
        if self.status != 'active':
            raise ValidationError(_("Course registration is only available for active courses."))

        if self.remaining_slots <= 0:
            raise ValidationError(_("No slots remaining in this course."))

        current_employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)], limit=1)
        if not current_employee:
            raise ValidationError(_("You must be an employee to register for courses."))

        if self.course_type == 'in_house' and not self.env.user.has_group('hr.group_hr_user'):
            raise ValidationError(
                _("Only HR department members can register participants for in-house courses."))

        if self.participant_ids.filtered(lambda p: p.employee_id.id == current_employee.id):
            raise ValidationError(_("You are already registered for this course."))

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

    # Basic state change actions
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
        if self.status != 'gd_approval':
            raise ValidationError(_("Only courses with General Director approval can be activated."))
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
        if self.status not in ['active', 'in_progress', 'staff_approval', 'hr_approval', 'fd_approval', 'gd_approval']:
            raise ValidationError(_("Only active or in-progress courses can be cancelled."))
        self.status = 'cancel'
        return True

    # Approval Actions - Consolidated into a single method
    def _show_approval_wizard(self, approval_level):
        """Common method to show approval wizard for any level"""
        self.ensure_one()

        approval = self.approval_ids.filtered(lambda a: a.approval_level == approval_level and a.status == 'waiting')
        if not approval:
            # Tạo approval mới cho level hiện tại
            current_user = self.env.user.employee_id
            approval = self.env['hmv.training.course.approval'].create({
                'training_course_id': self.id,
                'employee_id': current_user.id if current_user else 1,
                'approval_level': approval_level,
                'status': 'waiting',
                'sequence': 10
            })

        # Show approval wizard
        return {
            'name': 'Approval Comment',
            'type': 'ir.actions.act_window',
            'res_model': 'hmv.training.approval.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_training_course_id': self.id,
                'default_approval_id': approval.id,
                'default_action_type': 'approved',
                'default_approval_level': approval_level,
            }
        }
    # Specific approval actions that call the common method
    def action_staff_approve(self):
        return self._show_approval_wizard('staff')

    def action_hr_approve(self):
        return self._show_approval_wizard('hr_manager')

    def action_fd_approve(self):
        return self._show_approval_wizard('fd')

    def action_gd_approve(self):
        return self._show_approval_wizard('gd')

    def action_reject(self):
        """Reject the training course at current approval level"""
        self.ensure_one()

        # Get the current pending approval
        pending_approval = self.approval_ids.filtered(lambda a: a.status == 'waiting')
        if not pending_approval:
            raise ValidationError(_("No pending approval found to reject."))

        first_pending = min(pending_approval, key=lambda a: a.sequence)

        return {
            'name': 'Rejection Comment',
            'type': 'ir.actions.act_window',
            'res_model': 'hmv.training.approval.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_training_course_id': self.id,
                'default_approval_id': first_pending.id,
                'default_action_type': 'refused',
                'default_approval_level': self.current_approval_level,
            }
        }

    def send_confirmation_email(self):
        template = self.env.ref('hmv_training.email_template_training_confirmation')
        for participant in self.participant_ids.filtered(lambda p: p.status == 'waiting'):
            template.send_mail(participant.id, force_send=True)
        return True

    @api.depends('approval_ids')
    def _compute_current_approval(self):
        for record in self:
            pending_approvals = record.approval_ids.filtered(lambda a: a.status == 'waiting')
            record.current_approval_id = pending_approvals[0] if pending_approvals else False

    def action_submit(self):
        """Submit the training course for sequential approval workflow"""
        if self.status != 'draft':
            raise ValidationError(_("Only courses in 'Draft' state can be submitted for approval."))

        # Get approvers in the correct sequence
        approvers = self._get_approvers_sequence()
        if not approvers:
            raise ValidationError(_("No approvers found for this training course."))

        # Create approval records in sequence
        sequence = 10
        for approver in approvers:
            self.env['hmv.training.course.approval'].create({
                'training_course_id': self.id,
                'sequence': sequence,
                'employee_id': approver['employee_id'],
                'approval_level': approver['level'],
                'status': 'waiting'
            })
            sequence += 10

        # Update status to first approval stage
        self.write({
            'status': 'staff_approval'
        })

        return True

    def _get_approvers_sequence(self):
        """Return approvers in the correct sequence: Staff -> HR Manager -> FD -> GD"""
        approvers = []

        # 1. Staff approver (department manager)
        dept_manager = self.department_id.manager_id
        if dept_manager:
            approvers.append({
                'employee_id': dept_manager.id,
                'level': 'staff'
            })

        # 2. HR Manager
        hr_manager = self.env['hr.employee'].search([
            ('department_id.name', 'ilike', 'HR'),
            ('job_id.name', 'ilike', 'Manager')
        ], limit=1)
        if hr_manager:
            approvers.append({
                'employee_id': hr_manager.id,
                'level': 'hr_manager'
            })

        # 3. Finance Director
        fd = self.env['hr.employee'].search([
            ('job_id.name', 'ilike', 'Finance Director')
        ], limit=1)
        if fd:
            approvers.append({
                'employee_id': fd.id,
                'level': 'fd'
            })

        # 4. General Director
        gd = self.env['hr.employee'].search([
            ('job_id.name', 'ilike', 'General Director')
        ], limit=1)
        if gd:
            approvers.append({
                'employee_id': gd.id,
                'level': 'gd'
            })

        return approvers

