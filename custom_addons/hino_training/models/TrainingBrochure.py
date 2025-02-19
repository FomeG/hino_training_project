from odoo import models, fields

class TrainingBrochure(models.Model):
    _name = 'hmv.trainng.brochure'
    _description = 'Training Brochure'

    name = fields.Char(string="Brochure Name", required=True)
    # Các field khác...
