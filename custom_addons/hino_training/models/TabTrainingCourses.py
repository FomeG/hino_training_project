from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class TrainingCourses(models.Model):
    _name = 'hmv.training.course'
    _description = 'Training Courses Provided by Company'

    # Fields
    training_id = fields.Many2one('hmv.training.plan', string="Training Plan", invisible=True)
    courses = fields.Char(string="Courses", help="Hệ thống cho phép điền tên của khóa học")
    vendor_id = fields.Many2one(
        'res.partner',
        string="Vendor",
        domain=[('is_company', '=', True), ('active', '=', True)],
        help="Chọn nhà cung cấp chưa bị lưu trữ"
    )

    location_id = fields.Many2one('res.country.state', string="Location", domain=[('active', '=', True)], help="Chỉ cho chọn các tỉnh thành đang active")
    slot = fields.Integer(string="Slot", help="Hệ thống cho phép điền thông tin số lượng tối đa được phép đăng ký")
    # recommend_level_ids = fields.Many2many('hmv.list.value.line', string="Recommend level", domain=[('code', '=', 'LEVEL'), ('active', '=', True)], help="Chọn vị trí dự kiến trong List of Value")
    recommend_level_ids = fields.Char(string="Recomment level:",required=True)

    start_date = fields.Date(string="Start Date", default=fields.Date.today(), help="Không cho chọn thời gian trong quá khứ")
    end_date = fields.Date(string="End Date", help="Ngày dự kiến kết thúc, phải sau ngày bắt đầu")

    course_type = fields.Selection([
        ('in_house', 'In house'),
        ('public', 'Public')
    ], string="Type", help="Chọn loại khóa học")

    fee = fields.Float(string="Fee/per", help="Chi phí một người", compute="_compute_fee", store=True)
    estimated_fee = fields.Float(string="Estimated fee", compute="_compute_estimated_fee", store=True)
    other_fee = fields.Float(string="Other fee", help="Chi phí khác")
    
    # List of participants (related field, not editable directly)
    # participants = fields.One2many('hmv.training.course.participant', 'training_course_id', string="List of participants")
    participants = fields.Char(string="List of participants",required=True)

    @api.depends('course_type', 'slot', 'fee')
    def _compute_estimated_fee(self):
        for record in self:
            if record.course_type == 'public' and record.slot:
                record.estimated_fee = record.fee * record.slot
            else:
                record.estimated_fee = 0.0

    @api.depends('course_type')
    def _compute_fee(self):
        for record in self:
            if record.course_type == 'in_house':
                record.fee = 0.0
            # You could add additional logic if fee is determined from another source

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.end_date < record.start_date:
                raise ValidationError("End Date must be later than Start Date")
            if record.start_date < date.today():
                raise ValidationError("Start Date cannot be in the past")
