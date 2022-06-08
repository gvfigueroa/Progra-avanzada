import json
from os.path import join


def leer_parametros(parametro):#, parametro):


    with open("parametros.json") as f:
        data = json.load(f)
    return data[parametro]

