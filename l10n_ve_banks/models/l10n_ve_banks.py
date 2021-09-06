# -*- coding: utf-8 -*-

from odoo import models, fields, api


class l10n_ve_banks(models.Model):
    _name = 'l10n.ve.banks'
    _description = "Venezuela's banks list"

    name = fields.Char("Bank Name")
    bank_code = fields.Char("Bank Code")

