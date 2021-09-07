# -*- coding: utf-8 -*-
import re

from odoo import models, fields, api
from odoo import exceptions, _
import json
import requests
from requests.auth import HTTPBasicAuth
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class studentOdooMoodle(models.Model):
    _inherit = "op.student"

    FORM_OF_PAYMENT = [
        ('paypal','Paypal'),
        ('banpluspayBS','BanplusPay (Bs)'),
        ('banpluspayUSD', 'BanplusPay (USD)'),
        ('bolivares','Transferencia'),
        ('pagomovil', 'Pago Movil'),
        ('zelle', 'Zelle'),
        ('banitsmo', 'Banitsmo'),
        ]

    COURSE_NAME = [
        ('ECGI', 'Estrategias Comunicacionales para la Gestión de Información'),
        ('ONCO', 'Los obstáculos de los negocios y cómo convertirlos en oportunidades'),
        ('LDPE', 'Liderazgo para el desarrollo personal y estratégico'),
        ('TG', 'Transformación Genial'),
        ]
    
    
    student_id = fields.Char(string='ID in Moodle', size=8)          #ID DEVUELTO POR MOODLE AL MOMENTO DE CREAR EL ESTUDIANTE
    student_rif = fields.Char(string='VAT', size=11)
    student_ci = fields.Char(string='DNI', size=8)
    reference_number = fields.Char(string='Reference')
    moodle_usr_name = fields.Char(string='Username in Moodle')       #NOMBRE DE USUARIO DEL ESTUDIANTE CREADO
    course_name = fields.Char(string='Course Name')
    full_course_name = fields.Char(string='Full Course Name')
    payment_platform = fields.Selection(FORM_OF_PAYMENT, 'Payment Platform')
    payment_platform_m2o = fields.Many2one('course.payment.platform', 'Payment Platform')
    nac_banks = fields.Char(string='Banks')
    course_price = fields.Char(string='Course Price')
    referido_ciexpro = fields.Char(string='Referred by')
    address =  fields.Char(string='Address', size=256)
    origin_bank = fields.Many2one('l10n.ve.banks', 'Origin Bank')
    is_owner = fields.Boolean('Student?')
    owner_name = fields.Char('Titular')
    owner_ci = fields.Char('Cédula:')
    price_in_bs = fields.Char('Price in Bs')
    currency = fields.Char('Currency')
    partner_id = fields.Many2one('res.partner', 'Partner', ondelete="cascade")
    email = fields.Char('Email Address')

    functions = {1: 'core_user_create_users',
                 2: 'core_user_get_users',
                 3: 'core_user_delete_users',
                 4: 'core_course_create_courses',
                 5: 'core_course_get_courses ',
                 6: 'core_user_update_users',
                 7: 'core_course_delete_courses',
                 8: 'enrol_manual_enrol_users',
                 9: 'enrol_self_enrol_user',
                 10: 'core_user_update_users',
                 11: 'core_course_get_courses_by_field',
                 12: 'core_course_get_categories',
                 13: 'core_role_assign_roles'}

    create_users = {"users[0][username]": "antonio.rojas",
                    "users[0][auth]": "manual",
                    "users[0][password]": "*Antonio21*",
                    "users[0][firstname]": "Antonio",
                    "users[0][lastname]": "Rojas",
                    "users[0][email]": "johandre23@hotmail.com",
                    "users[0][city]": "Caracas",
                    "users[0][country]": "VE"
                    }
    get_users = {"criteria[0][key]": "email",
                 "criteria[0][value]": "johandre23@estelio.com"}

    update_users = {"users[0][id]": 10204,
                    "users[0][email]": "johandre23@estelio.com",
                    "users[0][lastname]": "Salcedo"
                    }

    delete_users = {"userids[0]": 10193}

    create_courses = {"courses[0][fullname]": "Curso de prueba 2",
                      "courses[0][shortname]": "Prueba",
                      "courses[0][categoryid]": 1}


    get_categories = {"criteria[0][key]": "name",
                      "criteria[0][value]": "Desarrollo"}

    assign_roles = {"assignments[0][roleid]": 1,
                    "assignments[0][userid]": 10204}

    
    #editar
    #@api.model
    def write(self, vals):
        
        res = super(studentOdooMoodle, self).write(vals)        
        dict_update = {"users[0][id]" : self.student_id}
        to_update = ['first_name','last_name','email','city','country']
        
        for key in vals.keys():
            if key in to_update:
                dict_update["users[0]["+key+"]"] = vals[key]          
        
        if 'users[0][email]' in dict_update.keys():            
            new_email = self.validate_email_addrs(vals['email'], 'email')            
            if not new_email.get('email', False):
                raise exceptions.except_orm(
                    _('Excepción Interfase ODOO-MOODLE'),
                    _('Invalid e-mail. Please check the e-mail field and try again.'))              

        self.call_api(self.functions[6], dict_update)                
        return res
    
    #@api.model
    #def create(self, vals):
        #local_name = ""
        ##if not vals.get("first_name", False):
        #payment_platform_m2o = vals.get('payment_platform_m2o', False)
        #local_name = vals.get('name', False).split(" ")[0]
        #vals.update({"first_name": local_name})
        ##IF NOT COURSE SET BLANK
        #local_course_name = vals.get('course_name', "").split("-") if vals.get('course_name', "") else ""
        ##SET COURSE NAME
        #course_code = local_course_name[0] if local_course_name and len(local_course_name) > 1 else ''
        #vals.update({"full_course_name": self.get_course_name(course_code)})

        #SET COURSE PRICE del cliente
        #local_price = local_course_name[1] if local_course_name and len(local_course_name) > 1 else ''
        #vals.update({"course_price": local_price})

        #if payment_platform_m2o and payment_platform_m2o not in [2,4]:
        #    vals.update({"currency": '0', 'price_in_bs': '0'})

        #res = super(studentOdooMoodle, self).create(vals)
        #self.action_send_email(res)        
        
        #return res

    def get_course_name(self, value):
        default_value = ""
        for val in self.COURSE_NAME:
            if val[0] == value:
                default_value = val[1]
        return default_value

    #Funcion que valida pago por paypal y envía correo

    

    def action_send_email(self, obj=None):
        template = self.env.ref('moodle_odoo_int.email_template_student_record')
        if obj:
            for stdn in obj:
                template.send_mail(stdn.id, force_send=True)
        else:
            for stdn in self:
                template.send_mail(stdn.id, force_send=True)
        return True

    def call_api(self, function, values):
        
        ir_config_obj = self.env['ir.config_parameter']
        local_url = ir_config_obj.sudo().get_param('moodle_url')
        local_token = ir_config_obj.sudo().get_param('moodle_token')
        url = local_url + '&wstoken=' + local_token + \
              '&moodlewsrestformat=json' \
              '&wsfunction=' + function

        response = requests.get(url, params=values)
        r = json.loads(response.text)
        
        return r

    def validate_email_addrs(self, email, field):
        res = {}        
        mail_obj = re.compile(r"""
                \b             # comienzo de delimitador de palabra
                [\w.%+-]       # usuario: Cualquier caracter alfanumerico mas los signos (.%+-)
                +@             # seguido de @
                [\w.-]         # dominio: Cualquier caracter alfanumerico mas los signos (.-)
                +\.            # seguido de .
                [a-zA-Z]{2,3}  # dominio de alto nivel: 2 a 6 letras en minúsculas o mayúsculas.
                \b             # fin de delimitador de palabra
                """, re.X)     # bandera de compilacion X: habilita la modo verborrágico, el cual permite organizar
                               # el patrón de búsqueda de una forma que sea más sencilla de entender y leer.
        if mail_obj.search(email):
            res = {
                field:email
            }
        return res
        
    def validate_phone_number(self, mobile, field):
        res = {}
        mobile_obj = re.compile(r"""
                \b             # comienzo de delimitador de palabra
                [04]       # Debe empezar con 04
                +[1,2]{1}         # Seguido de 1 o 2
                [2,4,6]{1}            # Seguido de 2,4 o 6
                [0-9]{7}  # Seguido de 7 números entre 0 y 9 
                \b             # fin de delimitador de palabra
                """, re.X)     # bandera de compilacion X: habilita la modo verborrágico, el cual permite organizar
                               # el patrón de búsqueda de una forma que sea más sencilla de entender y leer.
        if mobile_obj.search(mobile):
            res = {
                field:mobile
            }
        return res

    def validate_rif(self, rif, field):
        res = {}
        if rif:
            rif_obj = re.compile(r"""
                 \b 
                 [V,E]
                 +[0-9]{7,9}
                 \b 
                 """, re.X)
            if rif_obj.search(rif):
                res = {
                    field: rif
                }
        return res
    #TODO SOBREESCRIBIR EL METODO UNLINK DEL ORM PARA QUE CUANDO SE ELIMINE
    # UN ESTUDIANTE SE ELIMINE EL REGISTRO QUE SE CREA EN res_partner

    def unlink(self):
        
        partner_obj = self.env['res.partner']
        student_ids = self.ids
        partner_ids = []

        for id in student_ids:
            student = self.search([('id', '=', id)])            
            partner_ids.append(student.partner_id.id)
            delete_users = {"userids[0]": int(student.student_id)}
            call = self.call_api(self.functions[3], delete_users)
        res = super(studentOdooMoodle, self).unlink()

        for pid in partner_ids:
            partner_obj.search([('id', '=', pid)]).unlink()

        return res

    
class courseOdooMoodle(models.Model):

    _inherit = "op.course"

    course_id = fields.Char('ID del curso en Moodle', size=8)          #ID DEVUELTO POR MOODLE AL MOMENTO DE CREAR EL ESTUDIANTE
    #qty_students = fields.Integer('max limit')

    functions = {1: 'core_user_create_users',
                 2: 'core_user_get_users',
                 3: 'core_user_delete_users',
                 4: 'core_course_create_courses',
                 5: 'core_course_get_courses ',
                 6: 'core_user_update_users',
                 7: 'core_course_delete_courses',
                 8: 'enrol_manual_enrol_users',
                 9: 'enrol_self_enrol_user',
                 10: 'core_user_update_users',
                 11: 'core_course_get_courses_by_field',
                 12: 'core_course_get_categories',
                 13: 'core_role_assign_roles'}

    @api.model
    def create(self, vals):
        #self.validate_qty()
        create_courses = {"courses[0][fullname]": vals["name"],
                        "courses[0][shortname]": vals["code"],
                        "courses[0][categoryid]": int(1)}
                 
        response = self.call_api(self.functions[4], create_courses)
        vals['course_id'] = response[0].get('id', None)
        res = super(courseOdooMoodle, self).create(vals)

        return res
    
    def call_api(self, function, values):
        ir_config_obj = self.env['ir.config_parameter']
        local_url = ir_config_obj.sudo().get_param('moodle_url')
        local_token = ir_config_obj.sudo().get_param('moodle_token')
        url = local_url + '&wstoken=' + local_token + \
              '&moodlewsrestformat=json' \
              '&wsfunction=' + function

        response = requests.get(url, params=values)
        r = json.loads(response.text)        
        return r

    def validate_qty(self):
        ir_config_obj = self.env['ir.config_parameter']
        max_qty = ir_config_obj.sudo().get_param('max_limit_x_course')
        if self.qty_students + 1 > int(max_qty):
            raise exceptions.except_orm(
                _('Excepción Interfase ODOO-MOODLE'),
                _('This course is already filled out. Please, try another course or contact us for more information.'))

class coursePaymentPlatform(models.Model):
    _name = 'course.payment.platform'

    name = fields.Char("Paymen Platform")
    payment_code = fields.Char("payment_code")