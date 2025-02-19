from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TrainingPlan(models.Model):
    _name = 'hmv.training.plan'
    _description = 'Training Plan'

    # Số kế hoạch đào tạo: tự động sinh theo sequence (ví dụ: New khi tạo mới)
    name = fields.Char(
        string="Training Plan No.",
        required=True,
        readonly=True,
        default=lambda self: _('New')
    )

    # Năm kế hoạch đào tạo
    year = fields.Char(
        string="Year",
        required=True,
    )

    # Tổng chi phí các khóa học (các khóa học của toàn văn phòng)
    total = fields.Float(
        string="Total training fee for office",
        required=True,
    )

    # Khóa học dự kiến (Many2one tham chiếu đến model hmv.trainng.brochure)
    # training_brochure_id = fields.Many2one(
    #     'hmv.trainng.brochure',
    #     string="Training Brochure",
    #     required=True,
    # )
    training_brochure_id2 = fields.Char(
        string="Training Brochure",
        required=True
    )
    # Tổng chi phí các khóa học theo từng tab
    # (Có thể bạn sẽ tính toán bằng công thức SUM các trường fee từ một model con liên quan)
    total_training_fee = fields.Float(
        string="Total training fee",
        required=True,
    )

    # Tên công ty: chỉ cho phép hệ thống tự động điền, không cho sửa
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
    )

    # Trạng thái: mặc định là draft, không cho sửa (và ẩn trên view theo yêu cầu)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('fd_processing', 'Fd Processing'),
            ('hr_manager_processing', 'Hr Manager Processing'),
            ('approved', 'Approved'),
            ('cancel', 'Cancel'),
        ],
        string="State",
        required=True,
        readonly=True,
        default='draft'
    )

    # Diễn giải
    description = fields.Text(
        string="Description",
        required=True,
    )

    # --- Các nút (button) hành động trên form view ---

  
    def action_edit(self):
        for record in self:
            if record.state in ['submitted', 'approved']:
                raise ValidationError(_('You can only edit a Training Plan that is not submitted or rejected.'))
        return True
    def action_save(self):
        """
        Cho phép lưu lại bản ghi Training Plan khi trạng thái là draft.
        """
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(_("Training Plan chỉ được phép lưu lại khi ở trạng thái chưa submit."))
        # Ở đây lưu ý: thao tác save (write) thường được Odoo xử lý tự động khi nhấn nút Lưu.
        # Nếu cần logic bổ sung thì thực hiện ở đây.
        return True

    def action_create_record(self):
        """
        Cho phép tạo bản ghi Training Plan mới.
        Phương thức này có thể mở form view để nhập thông tin.
        """
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Training Plan'),
            'res_model': 'training.plan',
            'view_mode': 'form',
            'target': 'current',
        }
    def action_send_approval(self):
            self.ensure_one()
            # Logic gửi duyệt
            self.state = 'approved'
            return True

    def action_fd_processing(self):
            self.ensure_one()
            # Logic hủy
            self.state = 'fd_processing'
            return True

    def action_print(self):
            self.ensure_one()
            # Logic in phiếu
            return True
    def action_cancel(self):
            self.ensure_one()
            # Logic in phiếu
            self.state='cancel'
            return True

    def action_Hr_Manager_Processing(self):
            self.ensure_one()
            # Logic từ chối
            self.state = 'hr_manager_processing'
            return True
    training_course_ids = fields.One2many('hmv.training.course', 'training_id', string="Training Courses")
