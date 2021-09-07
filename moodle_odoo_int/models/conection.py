#!/usr/bin/env python3
import urllib.request
import urllib.parse
import http.client
import json

def sw(x):
    clima = {
        'Thunderstorm': 'Tormenta',
        'Clouds': 'Nublado',
        'Clear': 'Despejado',
        'Haze': 'Niebla',
        'Mist': 'niebla'
    }
    return clima.get(x,x)
try:
#    url = "http://api.openweathermap.org/data/2.5/weather?" \
#          "id=3995465&units=metric&APPID=152b1599f3e42d9d0f559bf3cf348a2b&lang=en"
#moodle token usuario jose angel eduardo
    #url = "https://devacademia.ciexpro.website?" \
    #      "wstoken=a0c28cade80890bcc03350194edc75aa&lang=en"
    functionName = 'auth_email_get_signup_settings'
    url = 'https://devacademia.ciexpro.website/webservice/rest/server.php?' \
          'wstoken=a0c28cade80890bcc03350194edc75aa' \
          '&wsfunction=' + functionName + '&username=jose.eduardo&secret=D105.35.4m0r'
    print("URL")
    print(url)
    print("CONSULTANDO DATOS ...")
    f = urllib.request.urlopen(url, timeout=30)
    print(f.read().decode('utf-8'))

    print("Obteniendo json ...")
    djson = json.loads(f.read())
    print("Imprimiendo json")
    print(djson)
    print("buscando datos")
    print(djson['coord']['lon'])
    print(sw(djson['weather'][0]['main']))
except Exception as e:
    print(e)
    print('error al consultar datos')