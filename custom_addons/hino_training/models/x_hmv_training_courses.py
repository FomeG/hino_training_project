from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class TrainingCourses(models.Model):
    _inherit = 'hmv.training.courses'

    # Fields
    # training_id = fields.Many2one('hmv.training.plan', string="Training Plan")


    # recommend_level_ids = fields.Many2many('hmv.list.value.line', string="Recommend level", domain=[('code', '=', 'LEVEL'), ('active', '=', True)], help="Chọn vị trí dự kiến trong List of Value")
    recommend_level_ids = fields.Many2many(
        'hmv.list.value.line',
        'hmv_list_value_line_recommend_level_rel',  # Tên bảng trung gian
        'training_course_id',  # Khóa ngoại trỏ về model hiện tại (hmv.training.courses)
        'list_value_line_id', # Khóa ngoại trỏ về model hmv.list.value.line
        string="Recommend Levels",
        # domain=[('active', '!=', False)],  
        help="Select the recommended levels"
    )



    fee = fields.Float(string="Fee/per", help="Chi phí một người", compute="_compute_fee", store=True)
    estimated_fee = fields.Float(string="Estimated fee", compute="_compute_estimated_fee", store=True)
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
