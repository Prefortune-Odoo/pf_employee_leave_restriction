# -*- coding: utf-8 -*-
# from odoo import http


# class PfEmployeeLeaveRestriction(http.Controller):
#     @http.route('/pf_employee_leave_restriction/pf_employee_leave_restriction', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pf_employee_leave_restriction/pf_employee_leave_restriction/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pf_employee_leave_restriction.listing', {
#             'root': '/pf_employee_leave_restriction/pf_employee_leave_restriction',
#             'objects': http.request.env['pf_employee_leave_restriction.pf_employee_leave_restriction'].search([]),
#         })

#     @http.route('/pf_employee_leave_restriction/pf_employee_leave_restriction/objects/<model("pf_employee_leave_restriction.pf_employee_leave_restriction"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pf_employee_leave_restriction.object', {
#             'object': obj
#         })

