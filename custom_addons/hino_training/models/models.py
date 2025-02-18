from odoo import models, fields

class EmployeeCustom(models.Model):
    _name = 'hr.employee.custom'
    _description = 'Custom Employee Model'

    name = fields.Char(string="Tên", required=True)
    age = fields.Integer(string="Tuổi")
