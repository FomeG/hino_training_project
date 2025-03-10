from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date

class tabTrainingCourses(models.Model):
    _name = 'hmv.tab.training.courses.provided.by.company'
    _description = 'Training courses provided by company'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'course_title'

    training_plan_id = fields.Many2one(
        'hmv.training.plan',
        string='Training Plan',
        ondelete='cascade'
    )
    course_title = fields.Char(string='Course Title', required=False, tracking=True)
   # Danh sách học viên đã đăng ký (chứa các thông tin: Họ và tên, Email, Department, Position)
    participant_ids = fields.Many2many(
        'hr.employee',
        'training_course_participant_rel',  # Tên bảng quan hệ riêng cho trường này
        'training_course_id',               # Cột liên kết với model hiện tại
        'employee_id',                      # Cột liên kết với hr.employee
        string='List of Participants',
        compute='_compute_participant_ids',
        store=True
    )

    # Trường hiển thị số lượng học viên đã đăng ký
    participant_count = fields.Integer(
        string="Participant Count",
        compute="_compute_participant_count",
        store=True
    )

    @api.depends('course_title')
    def _compute_participant_ids(self):
        for record in self:
            if record.course_title:
                # Tìm các need line (hmv.training.need.company) có brochure line với course_name trùng với course_title của bản ghi này
                need_lines = self.env['hmv.training.need.company'].search([
                    ('training_brochure_line_id.course_name', '=', record.course_title)
                ])
                # Lấy danh sách nhân viên từ các need line tìm được
                record.participant_ids = need_lines.mapped('employee_id')
            else:
                record.participant_ids = [(5, 0, 0)]

    @api.depends('participant_ids')
    def _compute_participant_count(self):
        for record in self:
            # Đếm số lượng học viên từ danh sách participant_ids
            record.participant_count = len(record.participant_ids)
            
    recommend_level_ids = fields.Many2many(
        comodel_name='hmv.list.value.line',  # Model được liên kết
        relation='training_course_recommend_level_rel',  # Tên bảng trung gian
        column1='hmv_tab_training_courses_provided_by_company_id',  # Khóa chính của bảng hiện tại
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
   
    year = fields.Date(string='Year', required=False, tracking=True)

  
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
    # Lấy training_brochure_id từ training_plan_id
    training_brochure_id = fields.Many2one(
        'hmv.training.brochure',
        string="Training Need",
        related='training_plan_id.training_brochure_id',
        store=True
    )

    
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
    @api.onchange('course_type', 'fee', 'participant_count')
    def _onchange_estimated_fee(self):
        if self.course_type == 'public':
            self.estimated_fee = (self.fee or 0.0) * self.participant_count

    # @api.onchange('start_date', 'end_date')
    # def _check_dates(self):
    #     for record in self:
    #         if record.end_date < record.start_date:
    #             raise ValidationError("End Date must be later than Start Date")
    #         if record.start_date < date.today():
    #             raise ValidationError("Start Date cannot be in the past")
    #         if record.end_date and not record.start_date:
    #             raise ValidationError("Please enter the start date before the end date.")

class tabFactoryTraining(models.Model):
    _name = 'hmv.tab.factory.training'
    _description = 'Training courses provided by company'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'course_title'

    training_plan_id = fields.Many2one(
        'hmv.training.plan',
        string='Training Plan',
        ondelete='cascade'
    )
    course_title = fields.Char(string='Course Title', required=False, tracking=True)

    participant_ids = fields.Many2many(
        'hr.employee',
        'training_factory_participant_rel',  # Tên bảng quan hệ riêng cho trường này
        'training_factory_id',  # Cột liên kết với model hiện tại
        'employee_id',  # Cột liên kết với hr.employee
        string='List of Participants',
        compute='_compute_participant_ids',
        store=True
    )

    # Trường hiển thị số lượng học viên đã đăng ký
    participant_count = fields.Integer(
        string="Participant Count",
        compute="_compute_participant_count",
        store=True
    )

    @api.depends('course_title')
    def _compute_participant_ids(self):
        for record in self:
            if record.course_title:
                # Tìm các need line (hmv.training.need.factory) có brochure line với course_name trùng với course_title của bản ghi này
                need_lines = self.env['hmv.training.need.factory'].search([
                    ('training_brochure_line_id.course_name', '=', record.course_title)
                ])
                # Lấy danh sách nhân viên từ các need line tìm được
                record.participant_ids = need_lines.mapped('employee_id')
            else:
                record.participant_ids = [(5, 0, 0)]

    @api.depends('participant_ids')
    def _compute_participant_count(self):
        for record in self:
            # Đếm số lượng học viên từ danh sách participant_ids
            record.participant_count = len(record.participant_ids)

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
    year = fields.Char(string='Year', required=False, tracking=True)

    training_brochure_id = fields.Many2one('hmv.training.brochure.line', string='Training brochure',
                                           required=False, tracking=True)
    location_id = fields.Many2one('res.country.state', string='Location', required=False, tracking=True)
    employee_hr_id = fields.Many2one('hr.employee', string='Prepared', tracking=True, )
    deptcombine = fields.Text(string='DeptCombine', tracking=True)

    description = fields.Char(string='Description', store=True)
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

    fee = fields.Float(string="Fee/per", help="Chi phí một người")
    estimated_fee = fields.Float(string="Estimated fee")
    other_fee = fields.Float(string="Other fee", help="Chi phí khác")
    purpose = fields.Text(string='Purpose')

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

    @api.onchange('course_type', 'fee', 'participant_ids')
    def _onchange_estimated_fee(self):
        if self.course_type == 'public':
            # Tự động tính dựa trên fee * số lượng học viên đăng ký
            self.estimated_fee = (self.fee or 0.0) * self.participant_count
        # Nếu course_type là in_house, estimated_fee sẽ không tự động tính,
        # cho phép người dùng nhập giá trị thủ công.

    # @api.onchange('start_date', 'end_date')
    # def _check_dates(self):
    #     for record in self:
    #         if record.end_date < record.start_date:
    #             raise ValidationError("End Date must be later than Start Date")
    #         if record.start_date < date.today():
    #             raise ValidationError("Start Date cannot be in the past")
    #         if record.end_date and not record.start_date:
    #             raise ValidationError("Please enter the start date before the end date.")

class tabOther(models.Model):
    _name = 'hmv.tab.others'
    _description = 'Training courses provided by company'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'course_title'

    training_plan_id = fields.Many2one(
        'hmv.training.plan',
        string='Training Plan',
        ondelete='cascade'
    )
    course_title = fields.Char(string='Course Title', required=False, tracking=True)

    participant_ids = fields.Many2many(
        'hr.employee',
        'training_other_participant_rel',  # Tên bảng quan hệ riêng cho trường này
        'training_course_id',               # Cột liên kết với model hiện tại
        'employee_id',                      # Cột liên kết với hr.employee
        string='List of Participants',
        compute='_compute_participant_ids',
        store=True
    )

    # Trường hiển thị số lượng học viên đã đăng ký
    participant_count = fields.Integer(
        string="Participant Count",
        compute="_compute_participant_count",
        store=True
    )

    @api.depends('course_title')
    def _compute_participant_ids(self):
        for record in self:
            if record.course_title:
                # Tìm các need line (hmv.training.need.other) có brochure line với course_name trùng với course_title của bản ghi này
                need_lines = self.env['hmv.training.need.other'].search([
                    ('training_brochure_line_id.course_name', '=', record.course_title)
                ])
                # Lấy danh sách nhân viên từ các need line tìm được
                record.participant_ids = need_lines.mapped('employee_id')
            else:
                record.participant_ids = [(5, 0, 0)]

    @api.depends('participant_ids')
    def _compute_participant_count(self):
        for record in self:
            # Đếm số lượng học viên từ danh sách participant_ids
            record.participant_count = len(record.participant_ids)

    recommend_level_ids = fields.Many2many(
        comodel_name='hmv.list.value.line',  # Model được liên kết
        relation='training_other_recommend_level_rel',  # Tên bảng trung gian
        column1='hmv_tab_training_other_provided_by_company_id',  # Khóa chính của bảng hiện tại
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
    year = fields.Date(string='Year', required=False, tracking=True)
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

    fee = fields.Float(string="Fee/per", help="Chi phí một người")
    estimated_fee = fields.Float(string="Estimated fee")
    other_fee = fields.Float(string="Other fee", help="Chi phí khác")
    purpose = fields.Text(string='Purpose')

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

    @api.onchange('course_type', 'fee', 'participant_ids')
    def _onchange_estimated_fee(self):
        if self.course_type == 'public':
            self.estimated_fee = (self.fee or 0.0) * self.participant_count
    # @api.onchange('start_date', 'end_date')
    # def _check_dates(self):
    #     for record in self:
    #         if record.end_date < record.start_date:
    #             raise ValidationError("End Date must be later than Start Date")
    #         if record.start_date < date.today():
    #             raise ValidationError("Start Date cannot be in the past")
    #         if record.end_date and not record.start_date:
    #             raise ValidationError("Please enter the start date before the end date.")

class TabApprovalTraining(models.Model):
    _name = 'hmv.tab.approval.training'
    _description = 'Training Plan Approval'

    comment = fields.Char(string='Comment')

    training_plan_id = fields.Many2one('hmv.training.plan', string='Training Plan', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='Approver')
    job_id = fields.Many2one(
        'hr.job',
        string='Position',
        related='employee_id.job_id',
        store=True,
        help="Vị trí của người trong luồng phê duyệt"
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True,
        help="Phòng ban của người trong luồng phê duyệt"
    )

    status = fields.Selection([
        ('waiting', 'Waiting'),
        ('approved', 'Approved'),
        ('refused', 'Refused')
    ], string='Status', default='waiting')

    def action_approve(self):
        return {
            'name': 'Approval Confirmation',
            'type': 'ir.actions.act_window',
            'res_model': 'hmv.training.plan.comment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_training_plan_id': self.training_plan_id.id,
                'default_action_type': 'approve'
            }
        }

    def action_refuse(self):
        return {
            'name': 'Refusal Confirmation',
            'type': 'ir.actions.act_window',
            'res_model': 'hmv.training.plan.comment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_training_plan_id': self.training_plan_id.id,
                'default_action_type': 'refuse'
            }
        }