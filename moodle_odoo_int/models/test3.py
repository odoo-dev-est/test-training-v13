#!/usr/bin/env python3
import urllib.request
import urllib.parse
import http.client
import json
import requests

def call_api(self, function):
    functions = {1:'core_user_create_users',
            2:'core_user_get_users',
            3:'core_user_delete_users',
            4:'core_course_create_courses',
            5:'core_course_get_courses ',
            6:'core_user_update_users',
            7:'core_course_delete_courses',
            8:'enrol_manual_enrol_users',
            9:'enrol_self_enrol_user',
            10:'core_user_update_users',
            11:'core_course_get_courses_by_field',
            12:'core_course_get_categories',
            13:'core_role_assign_roles'}

    create_users = {"users[0][username]":"antonio.rojas",
        "users[0][auth]":"manual",
        "users[0][password]":"*Antonio21*",
        "users[0][firstname]":"Antonio",
        "users[0][lastname]":"Rojas",
        "users[0][email]":"johandre23@hotmail.com",
        "users[0][city]":"Caracas",
        "users[0][country]":"VE"
        }

    get_users = {"criteria[0][key]": "email",
            "criteria[0][value]":"johandre23@estelio.com"}

    update_users = {"users[0][id]":10204,
               "users[0][email]":"johandre23@estelio.com",
               "users[0][lastname]":"Salcedo"
               }

    delete_users = {"userids[0]": 10193}
    
    create_courses = {"courses[0][fullname]":"Curso de prueba 2",
            "courses[0][shortname]":"Prueba",
            "courses[0][categoryid]":1}

    courses_byfield = {"field":""}

#get_courses = {"options[ids][1]": 38}

    get_categories = {"criteria[0][key]":"name",
                  "criteria[0][value]" : "Desarrollo"}

    assign_roles = {"assignments[0][roleid]": 1,
                "assignments[0][userid]": 10204}

#id = input("Ingrese el id: ")
#get_courses = {"options[ids][0]": int(id)}

#n = input("Ingrese el número de la función: ")
#n = 12
#name = input("Ingrese el nombre de la funcion: ")

    url = 'https://devacademia.ciexpro.website/webservice/rest/server.php?' \
      '&wstoken=1659e88702efd3d648f635ab80d03806' \
      '&moodlewsrestformat=json' \
      '&wsfunction='+ functions[int(n)] 

    response = requests.get(url, params = assign_roles)
    r = json.loads(response.text)
#print(r)
    return r