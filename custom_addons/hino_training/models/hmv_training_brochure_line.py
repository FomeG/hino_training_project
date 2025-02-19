# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HMVTrainingBrochureLine(models.Model):
    _name = 'hmv.training.brochure.line'
    _description = 'Training Brochure Line'

    training_brochure_id = fields.Many2one('hr.training.brochure', string='Training Brochure', required=True, ondelete='cascade')

    course_id = fields.Many2one('hmv.training.courses',   string='Course', domain="[('status', 'in', ['active', 'in_progress'])]")
    course_name = fields.Char( string='Course Name', related='course_id.course_title')
    start_date = fields.Date( string='Start Date', related='course_id.start_date')
    end_date = fields.Date( string='End Date', related='course_id.end_date')


    training_type = fields.Selection([
        ('company', 'Company Courses'),
        ('factory', 'Factory Training'),
        ('other', 'Other')
    ], string='Tab Type', default='company', required=True)
