# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
class HMVTrainingBrochureLine(models.Model):
    _name = 'hmv.training.brochure.line'
    _description = 'Training Brochure Line'
    _rec_name = 'course_name'

 
    # Many2one field to the training brochure
    training_brochure_id_company = fields.Many2one('hmv.training.brochure', string='Training Brochure 1', ondelete='cascade')
    training_brochure_id_factory = fields.Many2one('hmv.training.brochure', string='Training Brochure 2', ondelete='cascade')
    training_brochure_id_other = fields.Many2one('hmv.training.brochure', string='Training Brochure 3', ondelete='cascade')

    # Add a new field
    course_name = fields.Char( string='Course Name')
    start_date = fields.Date( string='Start Date')
    end_date = fields.Date( string='End Date')

    # Apply the method to the create method
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

    # Api onchange method to check the dates
    @api.onchange('start_date', 'end_date', 'training_brochure_id_company', 'training_brochure_id_factory', 'training_brochure_id_other')
    def _check_dates(self):
        # Get the brochure corresponding to the training_brochure_id field
        training_brochure = None
        if self.training_brochure_id_company:
            training_brochure = self.training_brochure_id_company
        elif self.training_brochure_id_factory:
            training_brochure = self.training_brochure_id_factory
        elif self.training_brochure_id_other:
            training_brochure = self.training_brochure_id_other

        # Check if the brochure exists and has a start date
        if training_brochure and training_brochure.start_date:
            brochure_start_date = training_brochure.start_date

            # Change the datetime to date
            if isinstance(brochure_start_date, datetime):
                brochure_start_date = brochure_start_date.date()

            if self.start_date and self.start_date < brochure_start_date:
                raise ValidationError(
                    f"The start date cannot be earlier than the brochure's start date ({brochure_start_date}).")

            if self.start_date and self.end_date and self.end_date < self.start_date:
                raise ValidationError("The end date must be greater than or equal to the start date.")
