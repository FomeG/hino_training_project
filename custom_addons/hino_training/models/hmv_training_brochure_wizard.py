from odoo import models, fields, api


class HMVUpdateCoursesWizard(models.TransientModel):
    _name = 'hmv.update.courses.wizard'
    _description = 'Update Courses Wizard'

    course_ids = fields.Many2many(
        'hmv.training.courses',
        string='Courses',
        domain=[('status', 'in', ['active', 'in_progress'])]
    )

    def action_confirm(self):
        active_id = self.env.context.get('active_id')
        brochure = self.env['hmv.training.brochure'].browse(active_id)

        for course in self.course_ids:
            self.env['hmv.training.brochure.line'].create({
                'training_brochure_id_company': brochure.id,
                'course_name': course.course_title,
                'start_date': course.start_date,
                'end_date': course.end_date,
            })

        return {'type': 'ir.actions.act_window_close'}