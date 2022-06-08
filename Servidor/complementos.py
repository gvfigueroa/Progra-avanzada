from leer_archivo import leer_parametros

def logs(cliente, evento, detalles):
    #imprime los logs en la terminal
    print("-" * leer_parametros("largo_str"))
    client = '{:^25}'.format(cliente)
    event = '{:^25}'.format(evento)
    details = '{:^25}'.format(detalles)
    str = '|{}|{}|{}|'.format(client, event, details)
    print(str)

#def condicion_victoria()
def paridad(n):
        if n % 2 == 0:
            return "par"
        else:
            return "impar"

def comandos_resto(respuesta):
        #maneja la respusta a enviar para el resto de 
        #usuarios no involucrados en el mensaje en sí
        #Ej: actualizar ventana principal, actualizar botones, etc
        juego = respuesta["comando"] == "comenzar_juego"
        sala = respuesta["comando"] == "volver_sala_principal"
        apuestas = respuesta["comando"] == "turno_listo"
        if respuesta["comando"] == "ingreso":
            if respuesta["pase"]:
                respuesta["comando"] = "actualizar_sala_principal"
            else:
                respuesta["comando"] = "nada"
        elif respuesta["comando"] == "salir":
            respuesta["comando"] = "actualizar_sala_principal"
        elif respuesta["comando"] == "reto":
            respuesta["comando"] = "actualizar_botones"
        elif juego or sala:
            respuesta["comando"] = "volver_sala_principal"
        elif respuesta["comando"] == "turno_no_listo" or apuestas:
            respuesta["comando"] = "nada"
        elif respuesta["comando"] == "terminar_partida" or "mostrar_inicio":
            respuesta["comando"] = "nada"
        elif respuesta["comando"] == "salir_juego":
            respuesta["comando"] = "nada"
        elif respuesta["comando"] == "salida":
            respuesta["comando"] = "desconectar_terminal"
        return respuesta

