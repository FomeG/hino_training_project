from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date


class TrainingCourses(models.Model):
    _name = 'hmv.training.courses'
    _description = 'Training Courses'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    training_plan_id = fields.Many2one(
            'hmv.training.plan',
            string='Training Plan'
        )

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
    # training_method_id = fields.Many2one('hmv.list.value.line', string='Training Method', required=True,
    #                                      tracking=True, domain=[('code', '=', 'TRAINING_METHOD')]) ???? lấy ở đâu
    year = fields.Date(string='Year', required=True, tracking=True)
    # training_brochure_id = fields.Many2one('hmv.training.brochure.line', string='Training brochure',
    #                                        required=True, tracking=True)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
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
    ], string='Course Type', required=True, tracking=True)
    estimate_fee = fields.Monetary(string='Actual Fee', required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    # audience_ids = fields.Many2one('hmv.list.value.line', string='Audience', required=True,
    #                                tracking=True, domain=[('code', '=', 'TR_LEVEL')]) ???? lấy ở đâu
    participant_ids = fields.One2many('hmv.training.participant', 'course_id', string='Participants')

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

    @api.onchange('training_brochure_id')
    def _onchange_training_brochure_id(self):
        if self.training_brochure_id:
            self.course_type = self.training_brochure_id.course_type
            self.estimate_fee = self.training_brochure_id.estimate_fee

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
