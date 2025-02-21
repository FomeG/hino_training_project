# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HMVTrainingBrochureLine(models.Model):
    _name = 'hmv.training.brochure.line'
    _description = 'Training Brochure Line'

    training_brochure_id_company = fields.Many2one('hmv.training.brochure', string='Training Brochure 1', ondelete='cascade')
    training_brochure_id_factory = fields.Many2one('hmv.training.brochure', string='Training Brochure 2', ondelete='cascade')
    training_brochure_id_other = fields.Many2one('hmv.training.brochure', string='Training Brochure 3', ondelete='cascade')

    course_name = fields.Char( string='Course Name')
    start_date = fields.Date( string='Start Date')
    end_date = fields.Date( string='End Date')

    @api.model
    def create(self, vals):
        active_id = self.env.context.get('active_id')
        if active_id:
            if self.env.context.get('active_tab') == 'company_training':
                vals['training_brochure_id_company'] = active_id
            elif self.env.context.get('active_tab') == 'factory_training':
                vals['training_brochure_id_factory'] = active_id
            elif self.env.context.get('active_tab') == 'other_training':
                vals['training_brochure_id_other'] = active_id
        return super(HMVTrainingBrochureLine, self).create(vals)

