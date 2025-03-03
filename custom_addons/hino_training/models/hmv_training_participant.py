from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TrainingParticipant(models.Model):
    _name = 'hmv.training.participant'
    _description = 'Training Participant'

    course_id = fields.Many2one('hmv.training.courses', string='Training Course', ondelete='cascade')
    tab_training_courses = fields.Many2one('hmv.tab.training.courses.provided.by.company', string='tab_training_courses', ondelete='cascade')

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

    @api.constrains('employee_id', 'course_id')
    def _check_unique_employee_course(self):
        for record in self:
            duplicate = self.search([
                ('employee_id', '=', record.employee_id.id),
                ('course_id', '=', record.course_id.id),
                ('id', '!=', record.id)
            ])
            if duplicate:
                raise ValidationError(_("Employee %s is already registered for this course!") % record.employee_id.name)

    def action_confirm(self):
        for record in self:
            # Check if there are remaining slots before confirming
            confirmed_participants = self.env['hmv.training.participant'].search_count([
                ('course_id', '=', record.course_id.id),
                ('status', '=', 'agreed')
            ])

            # If the course's slot limit is reached, prevent confirmation
            if confirmed_participants >= record.course_id.slot:
                raise ValidationError(_("Cannot confirm participant: no remaining slots available for this course."))

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