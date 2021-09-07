# -*- coding: utf-8 -*-
###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import models, fields, api, _
from datetime import date, timedelta


class OpCourse(models.Model):
    _inherit = "op.course"

    course_description = fields.Text("Description")
    time_lapse = fields.Char("Time Lapse", default="2 Semanas", readonly=True)
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date", compute='_compute_end_date', store=True)

    @api.depends('start_date', 'time_lapse')
    def _compute_end_date(self):
        days_per_week = 7
        for d in self:
            weeks_number = int(d.time_lapse.split(" ")[0])
            if d.start_date:
                d.end_date = d.start_date + timedelta(days=weeks_number*7)

class OpCourseTopic(models.Model):
    _name = "op.course.topic"

    module_name = fields.Char("Topic Name", size=30)
    module_description = fields.Char("Topic Description", size=100)
