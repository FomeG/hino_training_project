from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
class HMVTrainingBrochure(models.Model):
    _name = 'hmv.training.brochure'
    _description = 'Training Brochure'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Fields
    code = fields.Char(string=' Training Brochure No.', readonly=True,  default=lambda self: self._get_default_code(), copy=False, tracking=True)
    name = fields.Char(string='Description', required=True, tracking=True)
    year = fields.Char(string='Year', compute='_compute_year', store=True)
    start_date = fields.Datetime( string='Registration Start Date',required=True, tracking=True, store=True)
    end_date = fields.Datetime( string='Registration End Date', tracking=True)
    created_on = fields.Datetime(string='Created On', readonly=True, default=fields.Datetime.now)
    employee_id = fields.Many2one('hr.employee', string='Creator', default=lambda self: self.env.user.employee_id, required=True, tracking=True)
    company_id = fields.Many2one( 'res.company', string='Company', default=lambda self: self.env.company, required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='State', default='draft', tracking=True)

    # Tabs
    company_training_ids = fields.One2many('hmv.training.brochure.line', 'training_brochure_id',
                                           string='Company Training Courses',
                                           domain=[('training_type', '=', 'company')])

    factory_training_ids = fields.One2many('hmv.training.brochure.line', 'training_brochure_id',
                                           string='Factory Training',
                                           domain=[('training_type', '=', 'factory')])

    other_training_ids = fields.One2many('hmv.training.brochure.line', 'training_brochure_id',
                                         string='Other Training',
                                         domain=[('training_type', '=', 'other')])

    # Sequence Generation
    def _get_default_code(self):
        # Lấy giá trị mặc định từ ir.sequence
        return self.env['ir.sequence'].next_by_code('hmv.training.brochure.code') or 'CP0001'

    @api.model
    def create(self, vals):
        # Gán mặc định cho trường code khi tạo bản ghi
        if not vals.get('code'):
            vals['code'] = self._get_default_code()
        return super(HMVTrainingBrochure, self).create(vals)

    # Action Methods
    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_update_courses(self):
        pass

    @api.depends('start_date')
    def _compute_year(self):
        for record in self:
            if record.start_date:
                record.year = fields.Datetime.from_string(record.start_date).strftime('%Y')
            else:
                record.year = 0

    @api.constrains('start_date', 'end_date', 'created_on')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.created_on and record.start_date < record.created_on:
                raise ValidationError("The start date must be greater than or equal to the created on date.")
            if record.end_date and record.start_date and record.end_date < record.start_date:
                raise ValidationError("The end date must be greater than or equal to the start date.")