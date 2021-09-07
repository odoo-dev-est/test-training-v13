# coding: utf-8

import csv
import codecs
import io
import os
import base64

from odoo.osv import  osv
from odoo import api, fields, models, _



class PaymentsImportBankData(models.TransientModel):
    _name = 'payment.import.bank.data'
    _description = "Wizard that import file csv with data bank"

    def import_file_csv(self):
        """ Import file csv
        """
        separator = ','
        encoding = 'utf-8'
        lines = ''
        csv_data = None
        cont = 0
        payment_ids = self.env['banplus.payment'].search([('payment_platform', 'in', ('banpluspayBS','banpluspayUSD')),('status', '=', 'pendiente'),('is_valid', '=', False)])

        context = dict(self._context or {})

        if not self.sure:
            raise osv.except_osv(
                _("Error!"),
                _("Please confirm that you want to do this by checking the option"))

        p, ext = os.path.splitext(self.name)
        if not ext.lower() == '.csv':
            raise osv.except_osv(
                _("Error!"),
                _("Failed to read file. Unsupported file format, import only supports CSV"))

        file = self.csv_file
        try:
            csv_data = base64.decodestring(file)
        except:
            pass

        if csv_data:
            try:
                content = csv_data.decode(encoding)
                lines = content.split("\n")
            except:
                pass

            if lines and payment_ids:
                for line in lines:
                    data = line.split(separator)
                    reference = data[0]
                    cont += 1
                    if cont > 1:
                        for payment in payment_ids:
                            ref_number = payment.reference_number
                            if ref_number and str(ref_number) == str(reference):
                                payment.write({'status':'aprobada', 'is_valid':True})
                                break

        return {}

    name = fields.Char(string='File name')
    sure = fields.Boolean(string='Are you sure?')
    csv_file = fields.Binary(string='Import CSV')


