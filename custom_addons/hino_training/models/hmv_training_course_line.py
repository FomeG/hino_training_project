from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class TrainingParticipant(models.Model):
    _name = 'hmv.training.participant'
    _description = 'Training Participant'

    course_id = fields.Many2one('hmv.training.courses', string='Training Course', ondelete='cascade')
    tab_training_courses = fields.Many2one('hmv.tab.training.courses.provided.by.company', string='tab_training_courses', ondelete='cascade')
    training_brochure_line_id = fields.Many2one(
        'hmv.training.brochure.line',
        string='Training Brochure Line',
        related='course_id.training_brochure_id',
        store=True
    )
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

    @api.constrains('employee_id', 'course_id', 'training_brochure_line_id')
    def _check_unique_employee_course(self):
        for record in self:
            duplicate = self.search([
                ('employee_id', '=', record.employee_id.id),
                ('course_id', '=', record.course_id.id),
                ('training_brochure_line_id', '=', record.training_brochure_line_id.id),
                ('id', '!=', record.id)
            ])
            if duplicate:
                raise ValidationError(
                    _("Employee %s is already registered for this course from the same brochure line!")
                    % record.employee_id.name
                )

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

    def action_resend_email(self):
        """Resend notification email to the participant"""
        self.ensure_one()

        if not self.email:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Warning'),
                    'message': _('No email address found for this participant.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }

        mail_values = {
            'subject': f'Training Course Notification: {self.course_id.course_title}',
            'email_from': self.env.user.email or self.env.company.email,
            'email_to': self.email,
            'body_html': f"""
                <div style="margin: 0px; padding: 0px;">
                    <p style="margin: 0px; padding: 0px; font-size: 13px;">
                        Dear {self.full_name},
                        <br/><br/>
                        This is a notification regarding the Training Course: {self.course_id.course_title}
                        <br/><br/>
                        Details:
                        <ul>
                            <li>Course Title: {self.course_id.course_title}</li>
                            <li>Start Date: {self.course_id.start_date}</li>
                            <li>End Date: {self.course_id.end_date}</li>
                            <li>Vendor: {self.course_id.vendor_id.name if self.course_id.vendor_id else ''}</li>
                            <li>Training Method: {dict(self.course_id._fields['training_method'].selection).get(self.course_id.training_method) if hasattr(self.course_id, 'training_method') else ''}</li>
                            <li>Location: {self.course_id.location_id.name if hasattr(self.course_id, 'location_id') and self.course_id.location_id else ''}</li>
                        </ul>
                        <br/>
                        Please confirm your participation at your earliest convenience.
                        <br/><br/>
                        Best regards,<br/>
                        {self.env.user.name}
                    </p>
                </div>
            """
        }

        # Create and send email
        self.env['mail.mail'].create(mail_values).send()

        # Show success message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Notification email sent to %s') % self.full_name,
                'type': 'success',
                'sticky': False,
            }
        }