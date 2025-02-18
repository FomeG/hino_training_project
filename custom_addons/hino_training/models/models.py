# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class hino_training(models.Model):
#     _name = 'hino_training.hino_training'
#     _description = 'hino_training.hino_training'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

