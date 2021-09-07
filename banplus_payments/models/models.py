# -*- coding: utf-8 -*-

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api
from odoo import exceptions, _
from odoo.exceptions import UserError
import json
import requests
from requests.auth import HTTPBasicAuth
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime
from woocommerce import API
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class paymentModel(models.Model):
    
    _name = 'banplus.payment'
    _description = 'Payments'

    FORM_OF_PAYMENT = [
        ('paypal', 'Paypal'),
        ('banpluspayBS', 'BanplusPay (Bs)'),
        ('banpluspayUSD', 'BanplusPay (USD)'),
        ('bolivares', 'Transferencia'),
        ('pagomovil', 'Pago Movil'),
        ('zelle', 'Zelle'),
        ('banitsmo', 'Banitsmo'),
        ('paguelofacil', 'Paguelofacil'),
    ]
    DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
    
    status = fields.Char(string='Transaction state', size=10)
    date_time = fields.Datetime(string='Datetime')
    amount = fields.Float(string='Amount')
    is_valid = fields.Boolean (string='Validation', default=False)
    student_id = fields.Many2one('op.student',string='Student')
    full_course_name = fields.Char(string='Course Name')
    payment_platform = fields.Selection(FORM_OF_PAYMENT, 'Payment Platform')
    payment_platform_m2o = fields.Many2one('course.payment.platform', 'Payment Platform')
    nac_banks = fields.Char(string='Destination Bank')
    address =  fields.Char(string='Address', size=256)
    reference_number = fields.Char(string='Reference')
    moodle = fields.Boolean(string='Moodle', default=False)
    validation_date = fields.Datetime(string='Validation date')
    origin_bank = fields.Many2one('l10n.ve.banks', 'Origin Bank')
    is_owner = fields.Boolean('Student?')
    owner_name = fields.Char('Titular')
    owner_ci = fields.Char('Cédula')
    price_in_bs = fields.Char('Price in Bs')
    price_in_usd = fields.Char('Price in USD')
    currency = fields.Char('Currency')
    created_via = fields.Char('Created Via')
    date_completed = fields.Datetime(string='Date completed')
    date_paid = fields.Datetime(string='Date Paid')

    @api.model
    def create(self, vals):
        
        #local_reference = vals.get('reference_number', '')
        #pay_ids = self.search([('reference_number', '=', local_reference), ('student_id', '=', vals.get('student_id'))])
        #print(pay_ids)
        #if pay_ids:
        #    raise exceptions.except_orm(
        #        _('Excepción Banplus Payments'),
        #        _('El registro ya existe. Por favor verifique la información e intente nuevamente'))

        res = super(paymentModel, self).create(vals)        
        
        return res  
    
    def payment_validate(self):
        
        for student_item in self.search([('is_valid', '=', True),('moodle', '=', False)]):
            student_item.write({'moodle':True,'status':'aprobado'})
            student_item.student_id.is_valid = True
            student_item.write({'validation_date': datetime.now()})
            if not self.check_register(student_item.student_id):
                self.create_user_moodle(student_item.student_id)                        

    def check_register(self, students):
        
        get_users = {"criteria[0][key]": "email",
                    "criteria[0][value]": students.email
                    }        
        
        response = students.call_api(students.functions[2], get_users)
        
        if (len(response['users']) == 0):            
            return False
        else: 
            return response['users'][0]['id']

    def create_user_moodle(self, student):

        country_code = self.env['res.country'].search([('id', '=', student.country_id.id)])
        student.create_users.update({
            "users[0][username]": student.first_name.lower() + "." + student.last_name.lower(),
            "users[0][auth]": "manual",
            "users[0][password]": '*A21' + student.first_name + "." + student.last_name.lower(),
            "users[0][firstname]": student.first_name,
            "users[0][lastname]": student.last_name,
            "users[0][email]": student.email,
            "users[0][city]": student.city,
            "users[0][country]": country_code.code
        })

        response = student.call_api(student.functions[1], student.create_users)

        if isinstance(response, dict):  # & response.get('exception', False):
            raise exceptions.except_orm(
                _('Excepción pay_ids ODOO-MOODLE'),
                _(response['message']))
        else:
            student.student_id = response[0].get('id', None)
            student.moodle_usr_name = response[0].get('username', None)

    def get_woo_orders(self):
        student = None
        country_code=None
        student_dic = {}
        payment_dic = {}

        student_obj = self.env['op.student']
        payment_obj = self.env['banplus.payment']

        #print("entrando a get_woo_orders ...")
        local_url = self.env['ir.config_parameter'].sudo().get_param('woo_url_key')
        local_key = self.env['ir.config_parameter'].sudo().get_param('woo_consumer_key')
        local_secret = self.env['ir.config_parameter'].sudo().get_param('woo_consumer_secret_key')
        local_ver = self.env['ir.config_parameter'].sudo().get_param('woo_version_key')
        #print("Valores :", local_url, local_key, local_secret, local_ver)

        wcapi = API(
            url = local_url, 
            consumer_key = local_key,
            consumer_secret = local_secret,
            version = local_ver
        )
        #print("Llamando al API ...")
        r = wcapi.get("orders")
        orders = r.json()
        print("orders (r):",orders)
        for o in orders:
            #student_obj = None
            payment_dic['status'] = o['status']
            payment_dic['currency'] = o['currency']
            payment_dic['date_time'] = datetime.strptime(o['date_modified'], self.DATETIME_FORMAT) if o['date_modified'] else False
            payment_dic['address'] = o['billing']['address_1'] + ', ' +o['billing']['address_2']

            #buscando estudiante según los datos proporcionados
            #student_dic['first_name'] = o['billing']['first_name']
            #student_dic['last_name'] = o['billing']['last_name']
            #student_dic['email'] = o['billing']['email']
            student = student_obj.search([('first_name', '=', o['billing']['first_name']),
                                    ('last_name', '=', o['billing']['last_name']), 
                                    ('email', '=', o['billing']['email'])])
            print("student = ",student)
            #buscar el partner por su nombre
            if student:
                student_dic['mobile'] = o['billing']['phone']
                student_dic['city'] = o['billing']['city']
                country_code = self.env['res.country'].search([('code', '=', o['billing']['country'])])
                student_dic['country_id'] = country_code.id
                student_dic['partner_id'] = 3
                #student_dic['user_id'] = 2
                #student_dic['gender'] = 'o'
                print('student_dic', student_dic)
                student.write(student_dic)
                print('student = ', student)
                payment_dic['student_id'] = student.id

            #TODO Agregar metodos de pago nuevos al diccionario FORM_OF_PAYMENT
            payment_dic['payment_platform'] = o['payment_method']
            payment_dic['created_via'] = o['created_via']
            payment_dic['date_completed'] = datetime.strptime(o['date_completed'], self.DATETIME_FORMAT) if o['date_completed'] else False
            payment_dic['date_paid'] = datetime.strptime(o['date_paid'], self.DATETIME_FORMAT) if o['date_completed'] else False
            rate_usd = self.env['res.currency'].search([('name', '=', o['currency'])], limit=1).rate
            print("rate_usd = ", rate_usd)
            for line in o['line_items']:
                #Setting course price Value                
                print("line[total] = ", float(line['total']))
                if o['currency'] == 'USD':
                    payment_dic['price_in_usd'] = line['total']
                    payment_dic['amount'] = float(line['total'])
                    payment_dic['price_in_bs'] = payment_dic['amount']/rate_usd
                elif o['currency'] == 'VEF': #TODO Verificar el código de moneda que viene de Woocommerce
                    payment_dic['price_in_bs'] = float(line['total'])
                    payment_dic['price_in_usd'] = payment_dic['price_in_bs']*rate_usd
                    payment_dic['amount'] = payment_dic['price_in_bs']*rate_usd
                payment_dic['full_course_name'] = line['name']
                #Crea un pago por cada curso pagado en la plataforma 
                print('payment_dic = ', payment_dic)
                payment_obj.create(payment_dic)
            #break
    
    def get_user_id(self):
        partner = self.env['ir.config_parameter'].sudo().get_param('bp_pay_partner_value')
        partner_obj = self.env['res.partner'].search([('name', '=', partner)])
        if partner_obj:
            print('partner_obj = ', partner_obj)
            id = partner_obj.id
            print('partner_id = ', id)
            return id
        else:
            return 1

class student(models.Model):

    _inherit = "op.student"
    PAYMENT_STATUS = [
        ('aprobado','Aprobado'),
        ('rechazado','Rechazado'),
        ('pendiente','Pendiente')
        ]
    is_valid = fields.Boolean('Validación', default=False)

    ##@api.model
    ##def create(self, vals):
        
        ##payment_obj = self.env['banplus.payment']
        ##payment_dic = {}
        ##status = self.PAYMENT_STATUS[2][0]
        #Validacion de plataforma Paypal
        ##if (vals.get('payment_platform', False) == 'paypal'):
        #    if self.validate_paypal(vals):
        #        status = self.PAYMENT_STATUS[0][0]
        #        vals['is_valid'] = True
        #        payment_dic['is_valid'] = True               
        ##res = super(student, self).create(vals)

        #if not 'banpluspay' in vals.get('payment_platform', False):
        ##course_price = vals.get('course_price', 0)
        ##if course_price:
        ##    course_price = course_price.replace(',','.')
        ##amount = float(course_price)

        ##payment_dic['student_id'] = res.id
        ##payment_dic['status'] = status
        ##payment_dic['date_time'] = datetime.now()
        ##payment_dic['amount'] = amount
        ##payment_dic['full_course_name'] = vals.get('full_course_name', "")
        ##payment_dic['payment_platform'] = vals.get('payment_platform', "")
        ##payment_dic['reference_number'] = vals.get('reference_number', "")
        ##payment_dic['nac_banks'] = vals.get('nac_banks', "")
        ##payment_dic['address'] = vals.get('address', "")
        ##payment_dic['origin_bank'] = vals.get('origin_bank', False)
        ##payment_dic['payment_platform_m2o'] = vals.get('payment_platform_m2o', False)
        ##payment_dic['price_in_bs'] = vals.get('price_in_bs', '0,00')
        ##payment_dic['owner_name'] = vals.get('owner_name', '')
        ##payment_dic['owner_ci'] = vals.get('owner_ci', '')
        ##payment_dic['currency'] = vals.get('currency', '0,00')
        ##payment_obj.create(payment_dic)

        ##return res

    def validate_paypal(self, vals):
        #Bandera para saber si el pago fue completado con éxito
        is_success = False

        #Credencials
        client_id = "AS_mIqx-M5Qfl94G57No_Cwa7Ujv6Kn-9iGlHtCO1PlpD1bgjLNUo8MOYId1DmMYHuzi26k_upIrKvWL"
        client_secret = "EF-YIWjbVP_BhYb7YH9TD4BHIhM7qAIJR18e_nHw-w8HYztsdvM8QXRbirFmyRRVtgkIgPx9TRwmHoqF"

        #Prepare the field data 
        data ={
            'grant_type' : 'client_credentials'
            }
        
        #Call the api to obtain the access token
        login = requests.post('https://api-m.paypal.com/v1/oauth2/token', data = data, auth=HTTPBasicAuth(client_id, client_secret)).json()
        access_token = login["access_token"]
        
        #Prepare the header again with the access token
        headers_access_token = {
            'Content-Type': 'application/json', 
            'Authorization': f'Bearer {access_token}'  
            }

        #Call the api again but this time with the access token           
        api_orders = requests.get(f'https://api-m.paypal.com/v2/checkout/orders/{vals["reference_number"]}', headers = headers_access_token).json()


        order_status = api_orders["status"]
        #order_value = api_orders['purchase_units'][0]['amount']['value']

        style = """ * {
                font-family: Segoe UI;
                font-size: 16px;
                }
                .img > img {
                        width: 165px;
                }
                .title_pag {
                        text-align: center;
                        font-weight: 600;
                }
                .titleP {
                        text-align: center;
                        font-weight: 600;
                        padding: 0 45px 0 45px;
                }
                .conInf {
                        font-size: 14px;
                        padding-left: 15px;
                }
                .conCur {
                        text-align: center;
                        font-size: 14px;
                }"""

        if (order_status == 'COMPLETED'):

            message = Mail(from_email='no-reply@ciexpro.com',
               to_emails= vals['email'],
               subject='Verificación PayPal',
               plain_text_content='Esto es una prueba',
               html_content = f"""<head>
                        <meta charset="UTF-8" />
                        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                        <title>Document</title>
                        <style>{style}</style>
                        </head>
                        <body>
                        <div class="membrete">
                        <p>Estimado (a)</p>
                        <p><b> {vals['name']}</b></p>
                        <br />
                        </div>
                        <div>
                        <p class="title_pag">¡Gracias por su participación!</p>
                        <br />
                        </div>
                        <div>
                        <p style="text-align: justify">
                                Hemos confirmado el pago de su entrada al Bootcamp: 'Nombre_del_bootcamp'.
                        </p>
                        <p>
                                En el transcurso de los días se le enviará las credenciales de acceso.
                        </p>
                        <p>
                                Ante cualquier duda, consulte la sección Preguntas Frecuentes. También
                                puede comunicarse vía correo electrónico a
                                <b>soporte.bootcamps@ciexpro.com</b>
                        </p>
                        <br />
                        <br />
                        <br />
                        <table align="center">
                                <tr>
                                <td rowspan="2" style="border: 3px solid black">
                                <p class="titleP">Información del cliente</p>

                                <p class="conInf">{vals['name']}</p>
                                <p class="conInf">Monto: 'Monto del bootcamp'</p>
                                </td>
                                <td
                                style="
                                border-right: 3px solid black;
                                border-bottom: 3px solid black;
                                border-top: 3px solid black;
                                "
                                >
                                <p class="titleP">Detalles del pago</p>
                                <p class="conCur">Transferencia / Paypal</p>
                                </td>
                                <td
                                style="
                                border-right: 3px solid black;
                                border-bottom: 3px solid black;
                                border-top: 3px solid black;
                                "
                                >
                                <p class="titleP">Estatus de pago</p>
                                <p class="conCur">Confirmado</p>
                                </td>
                                </tr>
                                <tr>
                                <td
                                style="
                                border-right: 3px solid black;
                                border-bottom: 3px solid black;
                                "
                                >
                                <p class="titleP">{vals['reference_number']}</p>
                                <p class="conCur"></p>
                                </td>
                                </tr>
                        </table>
                        </div>
                        </body>"""

            )
            try:
                sg = SendGridAPIClient('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')
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response._headers)
            except Exception as e:
                print(str(e))  
            
            is_success = True

        else:
            message = Mail(from_email='no-reply@ciexpro.com',
               to_emails= vals['email'],
               subject='Verificación PayPal',
               plain_text_content='Esto es una prueba',
               html_content = f"""  <head>
                        <meta charset="UTF-8" />
                        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                        <style>{style}</style>
                        </head>
                        <body>
                        <div class="img">
                        </div>
                        <div class="membrete">
                        <p>Estimado (a)</p>
                        <p><b> {vals["name"]}</b></p>
                        <br />
                        </div>
                        <div>
                        <p class="title_pag">Su pago ha sido rechazado</p>
                        <br />
                        </div>
                        <div>
                        <p style="text-align: justify">
                                El pago registrado bajo el número de referencia <b>{vals["reference_number"]}</b> ha
                                presentado un error al momento de su verificación. Si el error sigue persistiendo,
                                le recomendamos que escriba a la plataforma de PayPal para solventar su inconveniente.
                        </p>
                        <br />
                        <br />
                        <br />
                        <table align="center">
                                <tr>
                                <td rowspan="2" style="border: 3px solid black">
                                <p class="titleP">Información del cliente</p>

                                <p class="conInf">{vals["name"]}</p>
                                <p class="conInf">Monto: "Aqui va el monto del Bootcamp"</p>
                                </td>
                                <td
                                style="
                                border-right: 3px solid black;
                                border-bottom: 3px solid black;
                                border-top: 3px solid black;
                                "
                                >
                                <p class="titleP">Detalles del pago</p>
                                <p class="conCur">Transferencia / Paypal</p>
                                </td>
                                <td
                                style="
                                border-right: 3px solid black;
                                border-bottom: 3px solid black;
                                border-top: 3px solid black;
                                "
                                >
                                <p class="titleP">Estatus de pago</p>
                                <p class="conCur">Rechazado</p>
                                </td>
                                </tr>
                                <tr>
                                <td
                                style="
                                border-right: 3px solid black;
                                border-bottom: 3px solid black;
                                "
                                >
                                <p class="titleP">{vals["reference_number"]}</p>
                                <p class="conCur"></p>
                                </td>
                                </tr>
                        </table>
                        </div>
                        </body> """
            )
        return is_success


    

   

    




