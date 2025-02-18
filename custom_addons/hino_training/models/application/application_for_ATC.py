from odoo import api, fields, models


class ApplicationForATC(models.Model):
    _name = 'application'
    _description = 'Application for Attending Training Course'

    name = fields.Char(string='Name')
