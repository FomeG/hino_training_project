from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class tabFactoryTraining(models.Model):
    _name = 'hmv.tab.factory.training'
    _description = 'Training courses provided by company'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    training_plan_id = fields.Many2one(
        'hmv.training.plan',
        string='Training Plan',
        ondelete='cascade'
    )
    course_title = fields.Char(string='Course Title', required=False, tracking=True)

    recommend_level_ids = fields.Many2many(
        comodel_name='hmv.list.value.line',  # Model được liên kết
        relation='training_tab_factory_recommend_level_rel',  # Tên bảng trung gian mới
        column1='hmv_tab_factory_training_id',  # Khóa chính của bảng hiện tại
        column2='list_value_line_id',  # Khóa chính của bảng liên kết
        string="Recommend Levels",
        help="Select the recommended levels"
    )

    start_date = fields.Date(string='Start date', required=False, tracking=True)
    end_date = fields.Date(string='End date', required=False, tracking=True)
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=False, tracking=True,
                                domain=[('is_company', '=', True)])
    purchase_order_id = fields.Many2one('purchase.order', string='Link PO', tracking=True)
    employee_id = fields.Many2many('hr.employee', string='P.I.C Staff/Dept', required=False,
                                   tracking=True)
    slot = fields.Integer(string='Slots', required=False, tracking=True)
    training_content = fields.Text(string='Training content', required=False, tracking=True)
    file_attach = fields.Binary(string='File Attach', attachment=True)
    confirmation_start_date = fields.Date(string='Start date of confirmation', required=False, tracking=True)
    confirmation_end_date = fields.Date(string='End date of confirmation', required=False, tracking=True)
    department_id = fields.Many2one('hr.department', string='Apply for department', required=False, tracking=True)
    # training_method_id = fields.Many2one('hmv.list.value.line', string='Training Method', required=False,
    #                                      tracking=True, domain=[('code', '=', 'TRAINING_METHOD')]) ???? lấy ở đâu
    year = fields.Date(string='Year', required=False, tracking=True)
    # training_brochure_id = fields.Many2one('hmv.training.brochure.line', string='Training brochure',
    #                                        required=False, tracking=True)
    
    training_brochure_id = fields.Many2one('hmv.training.brochure.line', string='Training brochure',
                                           required=False, tracking=True)
    location_id = fields.Many2one('res.country.state', string='Location', required=False, tracking=True)
    employee_hr_id = fields.Many2one('hr.employee', string='Prepared', tracking=True,)
    deptcombine = fields.Text(string='DeptCombine', tracking=True)
    description = fields.Text(string='Description', required=False, tracking=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('in_progress', 'In progress'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ], string='Status', required=False, default='draft', tracking=True)
    course_type = fields.Selection([
        ('public', 'Public'),
        ('in_house', 'In-house')
    ], string='Course Type', required=False, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    # audience_ids = fields.Many2one('hmv.list.value.line', string='Audience', required=False,
    #                                tracking=True, domain=[('code', '=', 'TR_LEVEL')]) ???? lấy ở đâu
    participant_ids = fields.One2many('hmv.training.participant', 'tab_training_courses', string='Participants')


    fee = fields.Float(string="Fee/per", help="Chi phí một người")
    estimated_fee = fields.Float(string="Estimated fee")
    other_fee = fields.Float(string="Other fee", help="Chi phí khác")
    purpose=fields.Text(string='Purpose')
    # List of participants (related field, not editable directly)
    # participants = fields.One2many('hmv.training.course.participant', 'training_course_id', string="List of participants")
    @api.depends('course_type', 'slot', 'fee')
    def _compute_estimated_fee(self):
        for record in self:
            if record.course_type == 'public' and record.slot:
                record.estimated_fee = record.fee * record.slot
            else:
                record.estimated_fee = 0.0

    @api.onchange('course_type')
    def _compute_fee(self):
        for record in self:
            if record.course_type == 'in_house':
                record.fee = 0.0
            # You could add additional logic if fee is determined from another source
    @api.onchange('course_type', 'fee', 'participant_ids')
    def _onchange_estimated_fee(self):
        if self.course_type == 'public':
            # Tự động tính dựa trên fee * số lượng học viên đăng ký
            self.estimated_fee = (self.fee or 0.0) * len(self.participant_ids)
        # Nếu course_type là in_house, estimated_fee sẽ không tự động tính,
        # cho phép người dùng nhập giá trị thủ công.

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.end_date < record.start_date:
                raise ValidationError("End Date must be later than Start Date")
            if record.start_date < date.today():
                raise ValidationError("Start Date cannot be in the past")
            
