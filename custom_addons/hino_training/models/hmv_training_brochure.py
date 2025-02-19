from odoo import models, fields, api, _


class HrTrainingBrochure(models.Model):
    _name = 'hmv.training.brochure'
    _description = 'Training Brochure'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Fields
    code = fields.Char(string=' Training Brochure No.', readonly=True, default=lambda self: _('New'), copy=False, tracking=True)
    name = fields.Char(string='Description', required=True, tracking=True)
    year = fields.Date(string='Year', compute='_compute_year', store=True)
    start_date = fields.Date( string='Registration Start Date',required=True, tracking=True)
    end_date = fields.Date( string='Registration End Date', tracking=True)
    created_on = fields.Date(string='Created On', required=True, default=fields.Datetime.now)
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
    @api.model
    def create(self, vals):
        if vals.get('code', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code('hr.training.brochure') or _('New')
        return super().create(vals)

    # Action Methods
    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_update_courses(self):
        active_courses = self.env['hmv.training.courses'].search([
            ('status', 'in', ['active', 'in_progress'])
        ])
        return {
            'name': 'Update Courses',
            'view_mode': 'form',
            'res_model': 'hmv.training.brochure',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_training_brochure_id': self.id,
                'default_training_course_id': active_courses.ids,
            }
        }

    @api.depends('start_date')
    def _compute_year(self):
        for record in self:
            if record.start_date:
                record.year = fields.Date.from_string(record.start_date).year
            else:
                record.year = 0