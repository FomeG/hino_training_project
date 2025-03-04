from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HMVTrainingBrochure(models.Model):
    _name = 'hmv.training.brochure'
    _description = 'Training Brochure'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    # Add a new field
    code = fields.Char(string=' Training Brochure No.', readonly=True, copy=False, tracking=True)
    name = fields.Char(string='Description', required=True, tracking=True)
    year = fields.Char(string='Year', compute='_compute_year', store=True)
    start_date = fields.Datetime( string='Registration Start Date',required=True, tracking=True, store=True)
    end_date = fields.Datetime( string='Registration End Date', tracking=True)
    created_on = fields.Datetime(string='Created On', readonly=True, default=fields.Datetime.now)
    employee_id = fields.Many2one('hr.employee', string='Creator', default=lambda self: self.env.user.employee_id, required=True, tracking=True)
    company_id = fields.Many2one( 'res.company', string='Company', readonly=True, compute='_compute_company', store=True)
    is_update_button_visible = fields.Boolean(string="Show Update Button", compute='_compute_is_update_button_visible', store=False)

    # Many2One relationships with the training brochure line
    company_training_ids = fields.One2many('hmv.training.brochure.line', 'training_brochure_id_company', string='Company Training Courses')
    factory_training_ids = fields.One2many('hmv.training.brochure.line', 'training_brochure_id_factory',string='Factory Training')
    other_training_ids = fields.One2many('hmv.training.brochure.line', 'training_brochure_id_other',string='Other Training')

    # Method to generate the next code
    def _get_next_code(self):
        sequence = self.env['ir.sequence'].sudo().search([('code', '=', 'hmv.training.brochure.code')], limit=1)
        if sequence:
            existing_codes = self.search([('code', 'ilike', 'CP')])
            if existing_codes:
                codes = [code.code for code in existing_codes]
                max_code = max(codes, key=lambda x: int(x[2:]))
                next_number = int(max_code[2:]) + 1
            else:
                next_number = sequence.number_next
                sequence.sudo().write({'number_next': next_number + 1})
            return f"{sequence.prefix or ''}{str(next_number).zfill(sequence.padding)}"
        return 'CP0001'

    # Apply the method to the create method
    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self._get_next_code()
        return super().create(vals)

    # Api onchange method to generate the next code
    @api.onchange('code')
    def _onchange_code(self):
        if not self.code:
            self.code = self._get_next_code()

    # Api onchange method to check the dates
    @api.onchange('start_date', 'end_date', 'created_on')
    def _check_dates(self):
        for record in self:
            if record.start_date and record.created_on:
                if record.start_date < record.created_on:
                    raise ValidationError("The start date must be greater than or equal to the created on date.")

            if record.start_date and record.end_date:
                if record.end_date < record.start_date:
                    raise ValidationError("The end date must be greater than or equal to the start date.")
                if record.end_date.year != record.start_date.year:
                    raise ValidationError("The end date must be within the same year as the start date.")

            if record.end_date and not record.start_date:
                raise ValidationError("Please enter the start date before the end date.")

    # Api onchange method to check the year
    @api.onchange('year')
    def _onchange_year(self):
        if self.year:
            existing_record = self.search([('year', '=', self.year)], limit=1)
            if existing_record:
                raise ValidationError(f"Training Brochure for {self.year} are available. Please select another year start date.")

    # Compute method to calculate the year
    @api.depends('start_date')
    def _compute_year(self):
        for record in self:
            record.year = str(record.start_date.year) if record.start_date else 0

    # Compute method to calculate the company
    @api.depends('employee_id')
    def _compute_company(self):
        for record in self:
            if record.employee_id:
                record.company_id = record.employee_id.company_id

    # Compute method to check if the update button is visible
    @api.depends('end_date', 'name', 'start_date', 'employee_id')
    def _compute_is_update_button_visible(self):
        for record in self:
            record.is_update_button_visible = bool(record.end_date and record.name and record.start_date and record.employee_id)

    # Method to open a wizard to select active courses to add to the brochure
    def action_update_courses(self):
        """Opens a wizard to select active courses to add to the brochure"""
        return {
            'name': 'Update Courses',
            'type': 'ir.actions.act_window',
            'res_model': 'hmv.update.courses.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_id': self.id,
                'active_model': 'hmv.training.brochure'
            }
        }








