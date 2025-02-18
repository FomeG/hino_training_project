from odoo import models, fields, api, _
from odoo.exceptions import UserError

class TrainingPlan(models.Model):
    _name = 'training.plan'
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
    training_brochure_id = fields.Many2one(
        'hmv.trainng.brochure',
        string="Training Brochure",
        required=True,
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
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
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
        """
        Cho phép sửa bản ghi Training Plan khi chưa submit
        hoặc khi phiếu bị từ chối (rejected).
        """
        for rec in self:
            if rec.state not in ['draft', 'rejected']:
                raise UserError(_("Training Plan chỉ được phép sửa khi chưa submit hoặc khi phiếu đã bị từ chối."))
        # Thực hiện các logic cần thiết để chuyển qua chế độ edit
        return True

    def action_save(self):
        """
        Cho phép lưu lại bản ghi Training Plan khi trạng thái là draft.
        """
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Training Plan chỉ được phép lưu lại khi ở trạng thái chưa submit."))
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
