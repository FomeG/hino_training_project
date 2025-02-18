# -*- coding: utf-8 -*-
# from odoo import http


# class HinoTraining(http.Controller):
#     @http.route('/hino_training/hino_training', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hino_training/hino_training/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hino_training.listing', {
#             'root': '/hino_training/hino_training',
#             'objects': http.request.env['hino_training.hino_training'].search([]),
#         })

#     @http.route('/hino_training/hino_training/objects/<model("hino_training.hino_training"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hino_training.object', {
#             'object': obj
#         })

