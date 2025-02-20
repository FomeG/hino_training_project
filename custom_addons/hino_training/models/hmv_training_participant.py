from odoo import models, fields, api, _


class TrainingParticipant(models.Model):
    _name = 'hmv.training.participant'
    _description = 'Training Participant'

    course_id = fields.Many2one('hmv.training.courses', string='Training Course', ondelete='cascade')
    # # lấy từ training need
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    full_name = fields.Char(related='employee_id.name', string='Full Name', readonly=True, store=True)
    email = fields.Char(related='employee_id.work_email', string='Email', readonly=True, store=True)
    position = fields.Char(related='employee_id.job_id.name', string='Position', readonly=True, store=True)
    department = fields.Char(related='employee_id.department_id.name', string='Department', readonly=True, store=True)


    status = fields.Selection([
        ('waiting', 'Waiting for confirmation'),
        ('refused', 'Refuse to participant'),
        ('agreed', 'Agree to participant')
    ], string='Status', default='waiting', tracking=True)

    def action_confirm(self):
        for record in self:
            record.status = 'agreed'
        return True

    def action_refuse(self):
        for record in self:
            record.status = 'refused'
        return True

    def action_resend(self):
        template = self.env.ref('hmv_training.email_template_training_confirmation')
        for record in self:
            template.send_mail(record.id, force_send=True)
        return True