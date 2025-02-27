from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TrainingPlan(models.Model):
    _name = 'hmv.training.plan'
    _description = 'Training Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    training_plan_line = fields.One2many(
        'hmv.training.plan.line',  # Tên model con
        'training_plan_id',        # Khóa ngoại trong model con
        string='Training Plan Lines'
    )
    tab_training_courses_id = fields.One2many(
        'hmv.tab.training.courses.provided.by.company',  # Tên model con
        'training_plan_id',        # Khóa ngoại trong model con
        string='Training Plan Lines'
    )
    tab_others_id = fields.One2many(
        'hmv.tab.others',  # Tên model con
        'training_plan_id',        # Khóa ngoại trong model con
        string='Training Plan Lines'
    )
    tab_factory_id = fields.One2many(
        'hmv.tab.factory.training',  # Tên model con
        'training_plan_id',        # Khóa ngoại trong model con
        string='Training Plan Lines'
    )
    # Khóa học dự kiến (Many2one tham chiếu đến model hmv.trainng.brochure)
    training_brochure_id = fields.Many2one(
        'hmv.training.brochure',
        string="Training Brochure",
        required=True,
    )
    # Số kế hoạch đào tạo: tự động sinh theo sequence (ví dụ: New khi tạo mới)
    name = fields.Char(string='Training plan No.', required=True, readonly=True, default='New')


    @api.depends('training_brochure_id.name')
    def _compute_name(self):
        for record in self:
            record.name = record.training_brochure_id.code if record.training_brochure_id else _('New')
    @api.model
    def create(self, vals):
        if not vals.get('name') or vals.get('name') == 'New':
            # Lấy mã tiếp theo từ sequence đúng cách
            sequence = self.env['ir.sequence'].next_by_code('hmv.training.plan') or 'TP0001'
            vals['name'] = sequence

        # Kiểm tra mã đã tồn tại và tự động tăng nếu bị trùng
        while self.search([('name', '=', vals['name'])], limit=1):
            # Tăng số cuối cùng thêm 1 nếu mã bị trùng
            prefix = ''.join(filter(str.isalpha, vals['name']))  # Lấy phần prefix chữ (VD: TP)
            number = ''.join(filter(str.isdigit, vals['name']))  # Lấy phần số

            # Nếu số không tồn tại, bắt đầu từ 1, ngược lại +1
            next_number = int(number) + 1 if number else 1
            # Tạo mã mới với padding 4 số
            vals['name'] = f"{prefix}{str(next_number).zfill(4)}"

        return super().create(vals)


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


    # training_brochure_id2 = fields.Char(
    #     string="Training Brochure",
    #     required=True
    # )
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
    # action report
    def action_print_training_courses(self):
        return self.env.ref('hino_training.action_report_training_plan').report_action(self)

    # def action_print_training_courses_detail(self):
    #     return self.env.ref('hino_training.action_report_training_courses').report_action(self)

    # Compute total money in training courses provided company
    total_estimated_fee = fields.Float(
            string="Total Estimated Fee", 
            compute="_compute_total_fees", 
            store=True
        )
    total_other_fee = fields.Float(
            string="Total Other Fee", 
            compute="_compute_total_fees", 
            store=True
        )
    total_fee = fields.Float(
            string="Grand Total", 
            compute="_compute_total_fees", 
            store=True
        )

    @api.depends('tab_training_courses_id.estimated_fee', 'tab_training_courses_id.other_fee')
    def _compute_total_fees(self):
            for record in self:
                total_estimated = sum(line.estimated_fee for line in record.tab_training_courses_id)
                total_other = sum(line.other_fee for line in record.tab_training_courses_id)
                record.total_estimated_fee = total_estimated
                record.total_other_fee = total_other
                record.total_fee = total_estimated + total_other

    # Compute total money in tab other
    total_estimated_fee_tab_other = fields.Float(
            string="Total Estimated Fee", 
            compute="_compute_total_fees_tab_other", 
            store=True
        )
    total_other_fee_tab_other = fields.Float(
            string="Total Other Fee", 
            compute="_compute_total_fees_tab_other", 
            store=True
        )
    total_fee_tab_other = fields.Float(
            string="Grand Total", 
            compute="_compute_total_fees_tab_other", 
            store=True
        )

    @api.depends('tab_others_id.estimated_fee', 'tab_others_id.other_fee')
    def _compute_total_fees_tab_other(self):
            for record in self:
                total_estimated = sum(line.estimated_fee for line in record.tab_others_id)
                total_other_fee= sum(line.other_fee for line in record.tab_others_id)
                record.total_estimated_fee_tab_other = total_estimated
                record.total_other_fee_tab_other = total_other_fee
                record.total_fee_tab_other = total_estimated + total_other_fee


   # Compute total money in tab factory
    total_estimated_fee_tab_factory = fields.Float(
            string="Total Estimated Fee", 
            compute="_compute_total_fees_tab_factory", 
            store=True
        )
    total_other_fee_tab_factory = fields.Float(
            string="Total Other Fee", 
            compute="_compute_total_fees_tab_factory", 
            store=True
        )
    total_fee_tab_factory  = fields.Float(
            string="Grand Total", 
            compute="_compute_total_fees_tab_factory", 
            store=True
        )

    @api.depends('tab_factory_id.estimated_fee', 'tab_factory_id.other_fee')
    def _compute_total_fees_tab_factory(self):
            for record in self:
                total_estimated = sum(line.estimated_fee for line in record.tab_factory_id)
                total_other_fee= sum(line.other_fee for line in record.tab_factory_id)
                record.total_estimated_fee_tab_factory = total_estimated
                record.total_other_fee_tab_factory = total_other_fee
                record.total_fee_tab_factory = total_estimated + total_other_fee
