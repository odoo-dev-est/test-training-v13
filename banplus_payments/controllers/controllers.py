# -*- coding: utf-8 -*-
# from odoo import http


# class BanplusPayment(http.Controller):
#     @http.route('/banplus_payment/banplus_payment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/banplus_payment/banplus_payment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('banplus_payment.listing', {
#             'root': '/banplus_payment/banplus_payment',
#             'objects': http.request.env['banplus_payment.banplus_payment'].search([]),
#         })

#     @http.route('/banplus_payment/banplus_payment/objects/<model("banplus_payment.banplus_payment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('banplus_payment.object', {
#             'object': obj
#         })
