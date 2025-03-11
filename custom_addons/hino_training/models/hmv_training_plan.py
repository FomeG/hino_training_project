from odoo import models, fields, api, _
from odoo.exceptions import ValidationError,UserError

class TrainingPlan(models.Model):
    _name = 'hmv.training.plan'
    _description = 'Training Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    tab_training_courses_id = fields.One2many(
        'hmv.tab.training.courses.provided.by.company',  # Tên model con
        'training_plan_id',        # Khóa ngoại trong model con
        string='Training Plan Lines',
        tracking=True

    )
    tab_others_id = fields.One2many(
        'hmv.tab.others',  # Tên model con
        'training_plan_id',        # Khóa ngoại trong model con
        string='Training Plan Lines',
        tracking=True

    )
    tab_factory_id = fields.One2many(
        'hmv.tab.factory.training',  # Tên model con
        'training_plan_id',        # Khóa ngoại trong model con
        string='Training Plan Lines',
        tracking=True
    )
    tab_approval_history_id = fields.One2many(
        'hmv.tab.approval.training',  # Tên model con
        'training_plan_id',        # Khóa ngoại trong model con
        string='Training Plan Lines',
        tracking=True
    )

    # Số kế hoạch đào tạo: tự động sinh theo sequence (ví dụ: New khi tạo mới)
    name = fields.Char(string='Training plan No.', required=True, readonly=True, default='New',tracking=True)
        # Năm kế hoạch đào tạo
    year = fields.Char(
        string="Year",
        required=True,
        tracking=True
    )

    training_brochure_id = fields.Many2one(
        'hmv.training.brochure',
        string="Training Brochure",
        required=True,
        tracking=True,
        domain="['|', ('year', '=', year), ('year', '=', False)]"
    )
    #created by for send mail
    created_by = fields.Many2one('res.users', string="Created By", default=lambda self: self.env.user)


    @api.onchange('training_brochure_id')
    def _onchange_training_brochure_id(self):
        if self.training_brochure_id:
            # Clear existing lines
            self.tab_training_courses_id = [(5, 0, 0)]
            self.tab_factory_id = [(5, 0, 0)]
            self.tab_others_id = [(5, 0, 0)]

            # Cập nhật tab_training_courses_id
            training_courses_lines = [(0, 0, {
                'course_title': line.course_name,
                'start_date': line.start_date,
                'end_date': line.end_date,
            }) for line in self.training_brochure_id.company_training_ids]

            # Cập nhật tab_factory_id
            factory_lines = [(0, 0, {
                'course_title': line.course_name,
                'start_date': line.start_date,
                'end_date': line.end_date,
            }) for line in self.training_brochure_id.factory_training_ids]

            # Cập nhật tab_others_id
            others_lines = [(0, 0, {
                'course_title': line.course_name,
                'start_date': line.start_date,
                'end_date': line.end_date,
            }) for line in self.training_brochure_id.other_training_ids]

            self.tab_training_courses_id = training_courses_lines
            self.tab_factory_id = factory_lines
            self.tab_others_id = others_lines
        else:
            # Nếu bỏ chọn brochure, xóa tất cả các dòng hiện tại
            self.tab_training_courses_id = [(5, 0, 0)]
            self.tab_factory_id = [(5, 0, 0)]
            self.tab_others_id = [(5, 0, 0)]
    @api.onchange('year')
    def _onchange_year(self):
        if self.year:
            return {
                'domain': {'training_brochure_id': [('year', '=', self.year)]}
            }
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




    # Tổng chi phí các khóa học (các khóa học của toàn văn phòng)
    total = fields.Float(
        string="Total training fee for office",
        compute="_compute_total_training_fee",
        store=True,
        tracking=True
    )


    # Tên công ty: chỉ cho phép hệ thống tự động điền, không cho sửa
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
        tracking=True
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('hr_manager_processing', 'Hr Manager Processing'),
            ('fd_processing', 'Fd Processing'),
            ('gd_processing', 'Gd Processing'),
            ('approved', 'Approved'),
            ('cancel', 'Cancel'),
        ],
        string="State",
        required=True,
        readonly=True,
        default='draft',
        tracking=True
    )
    description = fields.Char(
        string="Description",
        tracking=True

    )
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
   
    def action_cancel(self):
            self.ensure_one()
            self.state='cancel'
            return True


    # action report
    def action_print_training_courses(self):
        return self.env.ref('hino_training.action_report_training_factory').report_action(self)

    def action_print_training_courses_detail(self):
        return self.env.ref('hino_training.action_report_summary_plan').report_action(self)
    
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
            string="Total Other Fee ", 
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


    def action_hr_manager_approve(self):
        """HR Manager mở wizard để duyệt"""
        for record in self:
            if record.state == 'draft':
                return {
                    'name': _('HR Manager Approval'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'hmv.training.plan.comment.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_training_plan_id': record.id,  # Gửi ID sang wizard
                        'default_action_type': 'approve',
                    }
                }
        return True


    def action_submit(self):
        """Gửi duyệt lên HR Manager và hiển thị wizard"""
        if self.state != 'draft':
            raise ValidationError(_("Chỉ có thể gửi phê duyệt từ trạng thái 'Draft'."))

        return {
            'name': _('Approval Confirmation'),
            'type': 'ir.actions.act_window',
            'res_model': 'hmv.training.plan.comment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_training_plan_id': self.id,
                'default_action_type': 'approve'
            }
        }

    def action_send_approval(self):
        """HR Manager duyệt, gửi lên Finance Director và hiển thị wizard"""
        if self.state != 'hr_manager_processing':
            raise ValidationError(_("Chỉ có thể duyệt từ trạng thái 'HR Manager Processing'."))

        return {
            'name': _('Approval Confirmation'),
            'type': 'ir.actions.act_window',
            'res_model': 'hmv.training.plan.comment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_training_plan_id': self.id,
                'default_action_type': 'approve'
            }
        }

    def action_fd_processing(self):
        """Finance Director duyệt, chuyển sang trạng thái Approved và hiển thị wizard"""
        if self.state != 'fd_processing':
            raise ValidationError(_("Chỉ có thể duyệt từ trạng thái 'FD Processing'."))

        return {
            'name': _('Approval Confirmation'),
            'type': 'ir.actions.act_window',
            'res_model': 'hmv.training.plan.comment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_training_plan_id': self.id,
                'default_action_type': 'approve'
            }
        }
    def action_gd_processing(self):
        """Finance Director duyệt, chuyển sang trạng thái Approved và hiển thị wizard"""
        if self.state != 'gd_processing':
            raise ValidationError(_("Chỉ có thể duyệt từ trạng thái 'GD Processing'."))

        return {
            'name': _('Approval Confirmation'),
            'type': 'ir.actions.act_window',
            'res_model': 'hmv.training.plan.comment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_training_plan_id': self.id,
                'default_action_type': 'approve'
            }
        }


    def create_approval_record(self, state):
            """Tạo bản ghi lịch sử phê duyệt"""
            approver = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            self.env['hmv.tab.approval.training'].create({
                'training_plan_id': self.id,
                'employee_id': approver.id,
                'status': 'waiting' if state != 'approved' else 'approved'
            })
    def _get_next_state(self, current_state):
            """Xác định trạng thái tiếp theo của Training Plan"""
            state_mapping = {
                'draft': 'hr_manager_processing',
                'hr_manager_processing': 'fd_processing',
                'fd_processing': 'gd_processing',
                'gd_processing': 'approved'
            }
            return state_mapping.get(current_state, 'approved')
    def action_cancel(self):
        """ Khi ấn Reject thì chuyển trạng thái về Cancel """
        self.write({'state': 'draft'})

  
    @api.depends('total_fee', 'total_fee_tab_factory', 'total_fee_tab_other')
    def _compute_total_training_fee(self):
        for record in self:
            record.total = (record.total_fee or 0.0) + \
                        (record.total_fee_tab_factory or 0.0) + \
                        (record.total_fee_tab_other or 0.0)
     # Api onchange method to check the year
    @api.onchange('year')
    def _onchange_year(self):
        if self.year:
            existing_record = self.search([('year', '=', self.year)], limit=1)
            if existing_record:
                raise ValidationError(f"Training Plan {self.year} are available. Please select another year.")
            
    

    def action_send_mail_plan(self):
        for record in self:
            # Lấy email của người tạo
            creator_email = record.created_by.email
            if not creator_email:
                raise ValidationError("The creator does not have an email address.")

            # Tạo email để gửi
            mail_values = {
                'subject': 'Record Created Training Plan: %s' % record.name,
                'email_from': self.env.user.email or self.env.company.email,  # Email người gửi
                'email_to': creator_email,  # Email người nhận (người tạo bản ghi)
                'body_html': f"""
                           <p>Dear {record.created_by.name},</p>
                           <p>Your Training Plan: <strong>{record.name}</strong>  has been approved.</p>
                           <p>Best regards,<br/> {self.env.user.name}</p>
                       """
            }

            # Tạo và gửi email
            mail = self.env['mail.mail'].create(mail_values)
            mail.send()
        # Show success message with count of emails sent
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Notification emails sent to %s assignees') % len(self),
                'type': 'success',
                'sticky': False,
            }
        }
    