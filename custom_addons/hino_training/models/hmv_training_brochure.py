from odoo import models, fields, api
from odoo.exceptions import ValidationError
class HMVTrainingBrochure(models.Model):
    _name = 'hmv.training.brochure'
    _description = 'Training Brochure'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    # region Fields
    code = fields.Char(string=' Training Brochure No.', readonly=True,
                        copy=False, tracking=True)
    name = fields.Char(string='Description', required=True, tracking=True)
    year = fields.Char(string='Year', compute='_compute_year', store=True)
    start_date = fields.Datetime( string='Registration Start Date',required=True, tracking=True, store=True)
    end_date = fields.Datetime( string='Registration End Date', tracking=True)
    created_on = fields.Datetime(string='Created On', readonly=True, default=fields.Datetime.now)
    employee_id = fields.Many2one('hr.employee', string='Creator',
                                  default=lambda self: self.env.user.employee_id, required=True, tracking=True)
    company_id = fields.Many2one( 'res.company', string='Company', readonly=True, compute='_compute_company', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', tracking=True)
    is_update_button_visible = fields.Boolean(string="Show Update Button", compute='_compute_is_update_button_visible',
                                              store=False)
    # endregion
    # region Tabs
    company_training_ids = fields.One2many('hmv.training.brochure.line', 'training_brochure_id_company',
                                           string='Company Training Courses')

    factory_training_ids = fields.One2many('hmv.training.brochure.line', 'training_brochure_id_factory',
                                           string='Factory Training')

    other_training_ids = fields.One2many('hmv.training.brochure.line', 'training_brochure_id_other',
                                         string='Other Training')
    # endregion
    # region Api Method
    @api.model
    def create(self, vals):
        if not vals.get('code'):
            sequence = self.env['ir.sequence'].sudo().search([('code', '=', 'hmv.training.brochure.code')], limit=1)
            if sequence:
                next_number = sequence.number_next
                sequence.sudo().write({'number_next': next_number + 1})
                vals['code'] = f"{sequence.prefix or ''}{str(next_number).zfill(sequence.padding)}"
            else:
                vals['code'] = 'CP0001'

        existing_code = self.search([('code', '=', vals['code'])])
        if existing_code:
            raise ValidationError('Mã đã tồn tại trong hệ thống!')
        return super().create(vals)

    @api.onchange('code')
    def _onchange_code(self):
        if not self.code:
            sequence = self.env['ir.sequence'].sudo().search([('code', '=', 'hmv.training.brochure.code')], limit=1)
            if sequence:
                self.code = f"{sequence.prefix or ''}{str(sequence.number_next).zfill(sequence.padding)}"
            else:
                self.code = 'CP0001'

    @api.depends('start_date')
    def _compute_year(self):
        for record in self:
            if record.start_date:
                record.year = fields.Datetime.from_string(record.start_date).strftime('%Y')
            else:
                record.year = 0


    @api.onchange('start_date', 'end_date', 'created_on')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.created_on and record.start_date < record.created_on:
                raise ValidationError("The start date must be greater than or equal to the created on date.")
            if record.end_date and record.start_date and record.end_date < record.start_date:
                raise ValidationError("The end date must be greater than or equal to the start date.")
            

    # training_brochure_id = fields.One2many('hmv.training.courses', 'training_id', string="Training Courses")
            if record.start_date and record.created_on:
                if record.start_date < record.created_on:
                    raise ValidationError("The start date must be greater than or equal to the created on date.")

            if record.start_date and record.end_date:
                if record.end_date < record.start_date:
                    raise ValidationError("TThe end date must be greater than or equal to the start date.")

    @api.depends('employee_id')
    def _compute_company(self):
        for record in self:
            if record.employee_id:
                record.company_id = record.employee_id.company_id

    @api.depends('end_date', 'name', 'start_date', 'employee_id')
    def _compute_is_update_button_visible(self):
        for record in self:
            # Make the update button visible only when all fields have values
            record.is_update_button_visible = bool(
                record.end_date and record.name and record.start_date and record.employee_id)
    #endregion
    #region Action Methods
    def action_draff(self):
        self.write({'state': 'draft'})

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_update_courses(self):
        raise ValidationError("Update Courses is not implemented.")

    #endregion







