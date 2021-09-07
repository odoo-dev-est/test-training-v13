# -*- coding: utf-8 -*-
# from odoo import http


# class Submodules/moodleOdooInt(http.Controller):
#     @http.route('/submodules/moodle_odoo_int/submodules/moodle_odoo_int/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/submodules/moodle_odoo_int/submodules/moodle_odoo_int/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('submodules/moodle_odoo_int.listing', {
#             'root': '/submodules/moodle_odoo_int/submodules/moodle_odoo_int',
#             'objects': http.request.env['submodules/moodle_odoo_int.submodules/moodle_odoo_int'].search([]),
#         })

#     @http.route('/submodules/moodle_odoo_int/submodules/moodle_odoo_int/objects/<model("submodules/moodle_odoo_int.submodules/moodle_odoo_int"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('submodules/moodle_odoo_int.object', {
#             'object': obj
#         })
