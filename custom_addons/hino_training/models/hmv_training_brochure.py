from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HmvTrainingBrochure(models.Model):
    _name = 'hmv.training.brochure'
    _description = 'Training Brochure'

    # Sử dụng sequence để tự động tạo số cho Training Brochure với prefix CP
    code = fields.Char(
        string="Training Brochure No.",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code('hmv.training.brochure') or '/'
    )
    name = fields.Char(
        string="Description",
        required=True,
    )
    # Trường năm (bạn có thể thay đổi kiểu dữ liệu nếu cần lưu năm dưới dạng int hay string)
    year = fields.Integer(
        string="Year",
        required=True,
    )
    start_date = fields.Date(
        string="Course Registration Time",
        required=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string="Creator",
        default=lambda self: self.env.user.employee_id,
    )
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        default=lambda self: self.env.company,
        readonly=True,
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        string="State",
        default='draft',
    )
    # Nếu có mối liên hệ với Training Course, ví dụ sử dụng Many2many để liên kết các khóa đào tạo
    training_course_ids = fields.Many2many(
        'hmv.training.course',
        string="Training Courses",
    )

    # Button "Edit": chỉ cho phép sửa nếu trạng thái là draft hoặc rejected
    def action_edit(self):
        for record in self:
            if record.state not in ['draft', 'rejected']:
                raise UserError(_("Editing is allowed only when the record is in Draft or Rejected state."))
        # Thực hiện logic sửa nếu cần (ở đây chỉ trả về True để cho phép thao tác)
        return True

    # Button "Save": chỉ cho phép lưu nếu chưa submit (state = draft)
    def action_save(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_("Saving is allowed only when the record is in Draft state."))
        # Thực hiện các thao tác lưu bổ sung nếu cần
        return True

    # Button "Create": mở form tạo bản ghi mới
    def action_create_new(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Training Brochure'),
            'res_model': 'hmv.training.brochure',
            'view_mode': 'form',
            'target': 'current',
        }

    # Button "Update Course": kế thừa các khóa đào tạo ở trạng thái "Active" hoặc "In progress"
    def action_update_course(self):
        # Giả sử model khóa đào tạo là hmv.training.course và có trường state với các giá trị 'active' hoặc 'in_progress'
        training_courses = self.env['hmv.training.course'].search([
            ('state', 'in', ['active', 'in_progress'])
        ])
        if not training_courses:
            raise UserError(_("No active or in progress training courses found to update."))
        # Cập nhật trường liên kết: thêm các khóa đào tạo vừa tìm được vào danh sách
        self.training_course_ids = [(4, course.id) for course in training_courses]
        return True
