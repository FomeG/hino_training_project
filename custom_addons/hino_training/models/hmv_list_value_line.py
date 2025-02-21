from odoo import models, fields,api

class HMVListValueLine(models.Model):
    _name = 'hmv.list.value.line'
    _description = 'List Value Line'

    code = fields.Char(string="Code", required=True, help="Unique code for the value line")
    name = fields.Char(string="Name", required=True, help="Name of the value line")
    active = fields.Boolean(string="Active", default=True, help="Only active levels can be selected")


    @api.model
    def init(self):
        """ Tạo dữ liệu mặc định khi module được cài đặt """
        default_values = [
            {"code": "LV001", "name": "Level 1"},
            {"code": "LV002", "name": "Level 2"},
            {"code": "LV003", "name": "Level 3"},
        ]
        for val in default_values:
            if not self.env['hmv.list.value.line'].search([('code', '=', val["code"])]):
                self.env['hmv.list.value.line'].create(val)
