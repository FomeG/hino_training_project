from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TrainingPlanCommentWizard(models.TransientModel):
    _name = 'hmv.training.plan.comment.wizard'
    _description = 'Training Need Comment Wizard'

    approval_id = fields.Many2one('hmv.tab.approval.training', string='Approval')
    comment = fields.Text(string='Comment')
    action_type = fields.Selection([
        ('approve', 'Approve'),
        ('refuse', 'Refuse')
    ], string='Action Type', required=True)

    training_plan_id = fields.Many2one('hmv.training.plan', string='Training Plan', required=True)

    def action_confirm(self):
        """Xác nhận phê duyệt hoặc từ chối và lưu vào lịch sử"""
        self.ensure_one()
        
        if not self.training_plan_id:
            raise ValidationError(_('Please select a training plan.'))

        # Xác định trạng thái tiếp theo
        next_state = self.training_plan_id._get_next_state(self.training_plan_id.state)

        # Thêm vào lịch sử phê duyệt
        self.env['hmv.tab.approval.training'].create({
            'training_plan_id': self.training_plan_id.id,
            'employee_id': self.env.user.employee_id.id,
            'status': 'approved' if self.action_type == 'approve' else 'refused',
            'comment': self.comment,
        })

        # Cập nhật trạng thái của Training Plan nếu được duyệt
        if self.action_type == 'approve':
            self.training_plan_id.write({'state': next_state})
        elif self.action_type == 'refuse':
            self.training_plan_id.write({'state': 'cancel'})

        return {'type': 'ir.actions.act_window_close'}


    def action_cancel(self):
        """Đóng wizard"""
        return {'type': 'ir.actions.act_window_close'}