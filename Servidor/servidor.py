import json
import socket
import threading
import datetime
from random import choice, randint
from leer_archivo import leer_parametros
from complementos import logs, paridad, comandos_resto

class Servidor:
    _id_cliente = 1
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientes_conectados = {}
        self.clientes_sala_principal = {}
        self.juego = {}
        self.lock = threading.Lock()
        self.unir_y_escuchar()
        logs("Cliente", "Evento", "Detalles")

    def unir_y_escuchar(self):
        self.socket_servidor.bind((self.host, self.port))
        self.socket_servidor.listen()
        self.aceptar_conexiones()

    def aceptar_conexiones(self):
        thread = threading.Thread(target=self.thread_aceptar_conexiones)
        thread.start()

    def thread_aceptar_conexiones(self):
        while True:
            try:
                socket_cliente, _ = self.socket_servidor.accept()
                thread_escuchar_cliente = threading.Thread(
                    target=self.thread_escuchar_cliente,
                    args=(socket_cliente,),
                    daemon=True)
                thread_escuchar_cliente.start()
                logs(f"id :{self._id_cliente}", "Ingresó", "-")
                self._id_cliente += 1
            except ConnectionError:
                socket_cliente.close()
                break
            except OSError:
                respuesta = {}
                respuesta["comando"] = "desconexion_server"
                sockets = list(self.clientes_conectados.values())
                for socket in sockets:
                    self.enviar(respuesta, socket)
                break


    def thread_escuchar_cliente(self, socket_cliente):
        while True:
            respuesta = {}
            try:
                recibido = self.recibir_mensaje(socket_cliente)
                if len(recibido) == 0:
                    raise ConnectionError
                with self.lock:
                    respuesta = self.manejar_comando(recibido, socket_cliente)
                if len(respuesta) == 0:
                    raise ConnectionError
                sockets = self.comandar_envios(socket_cliente, respuesta)
                respuesta = comandos_resto(respuesta)
                self.actualizar_resto(sockets, respuesta)
            except ConnectionError:
                socket_cliente.close()
                break
            except json.JSONDecodeError:
                pass
            except TypeError:
                pass

    def comandar_envios(self, socket_cliente, respuesta):
        #maneja a quien enviarle el mensaje
        if "socket" in respuesta:
            sockets = respuesta["socket"]
            del respuesta["socket"]
        else:
            sockets = [socket_cliente]
        identificador = 1
        for socket in sockets:
            if identificador == 1:
                if "retado" in respuesta:
                    respuesta["soy"] = respuesta["retado"]
            else:
                if "retador" in respuesta:
                    respuesta["soy"] = respuesta["retador"]
            self.enviar(respuesta, socket)
            identificador += 1
        return sockets

    def actualizar_resto(self, sockets, respuesta):
        #enviar información al resto de usuarios
        for socket in self.clientes_sala_principal.values():
            if socket not in sockets:
                self.enviar(respuesta, socket)

    def recibir_mensaje(self, socket_cliente):
        #recibe mensaje y lo desencripta
        response_bytes_length = socket_cliente.recv(4)
        response_length = int.from_bytes(
            response_bytes_length, byteorder='little')
        response = bytearray()
        basura = bytearray()
        condicion = bytearray()
        indice = 0
        TAMANO_CHUNK = leer_parametros("tamano_chunk")
        while len(response) < response_length:
            numero_chunk = socket_cliente.recv(4)
            orden = int.from_bytes(numero_chunk, byteorder='big')
            read_length = min(TAMANO_CHUNK, response_length - len(response))
            indice += read_length
            response.extend(socket_cliente.recv(read_length))
            if read_length != TAMANO_CHUNK:
                basura.extend(socket_cliente.recv(TAMANO_CHUNK - read_length))
        condicion = response[indice - 1 : indice]
        response = response[:-1]
        mensaje_desencriptado = self.desencriptar_mensaje(response, condicion)
        received = self.decodificar_mensaje(mensaje_desencriptado)
        return received

    @staticmethod
    def codificar_mensaje(mensaje):
        try:
            mensaje_json = json.dumps(mensaje)
            mensaje_bytes = mensaje_json.encode("UTF-8")
            return bytearray(mensaje_bytes)
        except json.JSONDecodeError:
            pass

    @staticmethod
    def decodificar_mensaje(msg_bytes):
        try:
            mensaje = json.loads(msg_bytes)
            return mensaje
        except json.JSONDecodeError:
            pass

    #encripta mensaje
    def encriptar_mensaje(self, mensaje):
        partes = []
        for parte in range(3):
            i = parte
            partes.append(bytearray(b""))
            while i < len(mensaje):
                partes[parte].extend(mensaje[i : i + 1])
                i += 3
        if partes[1][0] > partes[2][0]:
            for parte in range(3):
                for i in range(len(partes[parte])):
                    if partes[parte][i : i + 1] == bytearray(b"\x05"):
                        partes[parte][i : i + 1] = bytearray(b"\x03")
                    elif partes[parte][i : i + 1] == bytearray(b"\x03"):
                        partes[parte][i : i + 1] = bytearray(b"\x05")
            ABCn = partes[0]
            ABCn.extend(partes[1])
            ABCn.extend(partes[2])
            ABCn.extend(bytearray(b"\x00"))
            return ABCn
        else:
            BACn = partes[1]
            BACn.extend(partes[0])
            BACn.extend(partes[2])
            BACn.extend(bytearray(b"\x01"))
            return BACn

    #desencripta mensaje
    def desencriptar_mensaje(self, mensaje, condicion):
        largo_mensaje = len(mensaje)
        largo_partes = []
        for parte in range(3):
            i = parte
            largo_partes.append(0)
            while i < len(mensaje):
                largo_partes[parte] += 1
                i += 3
        partes = []
        byte_ordenado = bytearray(b"")
        if condicion == b"\x00":
            largo = 0
            for parte in range(3):
                partes.append(bytearray(b""))
                partes[parte].extend(mensaje[largo : largo + largo_partes[parte]])
                largo += largo_partes[parte]
            i = 1
            indice = 0
            while i < len(mensaje):
                for parte in range(3):
                    byte_ordenado.extend(partes[parte][indice : indice + 1])
                    i += 1
                indice += 1
        elif condicion == b"\x01":
            largo_partes = [largo_partes[1], largo_partes[0], largo_partes[2]]
            largo = 0
            for parte in range(3):
                partes.append(bytearray(b""))
                partes[parte].extend(mensaje[largo : largo + largo_partes[parte]])
                largo += largo_partes[parte]
            partes_ordenadas = [partes[1], partes[0], partes[2]]
            i = 1
            indice = 0
            while i <= len(mensaje):
                for parte in range(3):
                    byte_ordenado.extend(partes_ordenadas[parte][indice : indice + 1])
                    i += 1
                indice += 1
        return bytes(byte_ordenado)
          
    def enviar(self, mensaje, sock_cliente):
        mensaje_codificado = self.codificar_mensaje(mensaje)
        mensaje_encriptado = self.encriptar_mensaje(mensaje_codificado)
        largo_mensaje = len(mensaje_encriptado).to_bytes(4, byteorder='little')
        TAMANO_CHUNK = leer_parametros("tamano_chunk")
        sock_cliente.send(largo_mensaje)
        numero_de_bloque = 0
        for i in range(0, len(mensaje_encriptado), TAMANO_CHUNK):
            chunk = bytearray(mensaje_encriptado[i : i + TAMANO_CHUNK])
            while len(chunk) < TAMANO_CHUNK:
                chunk.extend(bytearray(b"\x00"))
            numero_chunk = numero_de_bloque.to_bytes(4, byteorder='big')
            sock_cliente.send(numero_chunk + bytes(chunk))
            numero_de_bloque += 1
    
    def manejar_comando(self, recibido, socket_cliente):
        #maneja las respuestas recibidas
        comando = recibido["comando"]
        respuesta = {}
        if comando == "ingreso":
            respuesta["comando"] = "ingreso"
            condicion_1 = recibido["usuario"].isalnum() and len(recibido["usuario"]) >= 1
            condicion_2 = recibido["usuario"] not in self.clientes_conectados.keys()
            condicion_3 = len(self.clientes_sala_principal) < 4
            if condicion_1 and condicion_2 and condicion_3:
                try:
                    datetime.datetime.strptime(recibido["fecha"], '%d/%m/%Y')
                    self.clientes_sala_principal[recibido["usuario"]] = socket_cliente
                    self.clientes_conectados[recibido["usuario"]] = socket_cliente
                    respuesta["pase"] = True
                    respuesta["usuario"] = recibido["usuario"]
                    respuesta["usuarios"] = list(self.clientes_sala_principal.keys())
                    logs(recibido["usuario"], "Conectarse", "-")
                except ValueError as error:
                    respuesta["pase"] = False
                    logs(recibido["usuario"], "Fecha inválida", "-")
                    respuesta["usuario"] = ""
            else: 
                respuesta["pase"] = False
                logs(recibido["usuario"], "Usuario inválido", "-")
                respuesta["usuario"] = ""
        elif comando == "retar":
            respuesta["comando"] = "reto"
            respuesta["usuario"] = recibido["usuario"]
            respuesta["retado"] = recibido["retado"]
            respuesta["socket"] = [self.clientes_sala_principal[recibido["retado"]]]
            respuesta["indice"] = recibido["indice"]
            logs(recibido["usuario"], "Retó a", recibido["retado"])
        elif comando == "aceptar_reto":
            del self.clientes_sala_principal[recibido["retado"]]
            del self.clientes_sala_principal[recibido["retador"]]
            respuesta["comando"] = "comenzar_juego"
            respuesta["usuarios"] = list(self.clientes_sala_principal.keys())
            respuesta["retado"] = recibido["retado"]
            respuesta["retador"] = recibido["retador"]
            socket_1 = self.clientes_conectados[recibido["retado"]]
            socket_2 = self.clientes_conectados[recibido["retador"]]
            respuesta["socket"] = [socket_1, socket_2]
            turno = choice([respuesta["retado"], respuesta["retador"]])
            respuesta["turno"] = turno
            respuesta["avatar"] = randint(1, 2)
            logs(recibido["retado"], "Aceptó el reto de", recibido["retador"])
            logs(respuesta["turno"], "Comenzó su turno", "1")
        elif comando == "rechazar_reto":
            respuesta["comando"] = "volver_sala_principal"
            respuesta["usuarios"] = list(self.clientes_sala_principal.keys())
        elif comando == "salir":
            del self.clientes_sala_principal[recibido["usuario"]]
            del self.clientes_conectados[recibido["usuario"]]
            respuesta["comando"] = "salir"
            respuesta["pase"] = False
            respuesta["usuario"] = recibido["usuario"]
            respuesta["usuarios"] = list(self.clientes_sala_principal.keys())
        elif comando == "salir_juego":
            del self.clientes_conectados[recibido["usuario"]]
            respuesta["comando"] = "salir_juego"
            respuesta["pase"] = False
            respuesta["usuario"] = recibido["usuario"]
            respuesta["usuarios"] = list(self.clientes_sala_principal.keys())
        elif comando == "apuesta":
            jugadores = recibido["jugadores"]
            jugador = jugadores[0]
            oponente = jugadores[1]
            apuesta = recibido["apuesta"]
            apuesta_oponente = recibido["apuesta_oponente"]
            bolitas = recibido["bolitas"]
            turno = recibido["turno"]
            if apuesta_oponente != "no_en_turno":
                logs(jugador, "Confirmó su apuesta", apuesta)
                self.juego[jugador] = [apuesta, apuesta_oponente, jugadores, bolitas]
                if oponente in self.juego:
                    respuesta["turno"] = oponente
                    respuesta["comando"] = "turno_listo"
                    bol_apostadas = self.juego[oponente][0]
                    if paridad(bol_apostadas) == self.juego[jugador][1]:
                        respuesta["ganador"] = jugador
                        bol_ganador = bol_apostadas + bolitas[0]
                        bol_perdedor = bolitas[1] - bol_apostadas
                        bolitas_nuevas = [bol_ganador, bol_perdedor]
                        respuesta["perdedor"] = oponente
                        respuesta["bolitas"] = bolitas_nuevas
                        respuesta["apuestas"] = [apuesta, apuesta_oponente, 
                                                self.juego[oponente][0], 
                                                paridad(self.juego[oponente][0])]
                        logs(f"Partida: {jugador} vs {oponente}", "Ganador ronda", jugador)
                    else:
                        bol_apostadas = self.juego[jugador][0]
                        respuesta["ganador"] = oponente
                        bol_perdedor = bolitas[0] - bol_apostadas 
                        bol_ganador = bolitas[1] + bol_apostadas
                        bolitas_nuevas = [bol_ganador, bol_perdedor]
                        respuesta["perdedor"] = jugador
                        respuesta["bolitas"] = bolitas_nuevas
                        respuesta["apuestas"] = [self.juego[oponente][0], 
                                                paridad(self.juego[oponente][0]), 
                                                apuesta, apuesta_oponente]
                        logs(f"Partida entre {jugador} y {oponente}", "Ganador ronda", oponente)
                    socket_2 = self.clientes_conectados[oponente]
                    respuesta["socket"] = [self.clientes_conectados[jugador], socket_2]
                    del self.juego[jugador]
                    del self.juego[oponente]
                    for bolita in bolitas_nuevas:
                        if bolita >= 20:
                            respuesta["comando"] = "terminar_partida" 
                            del self.clientes_conectados[jugador]
                            del self.clientes_conectados[oponente]
                            logs("-", "Terminando partida", f"Ganador: {respuesta['ganador']}")
                            return respuesta
                    logs(oponente, "Comenzó su turno", "")
                else:
                    respuesta["comando"] = "turno_no_listo"
            else:
                self.juego[jugador] = [apuesta, jugadores]
                logs(jugador, "Confirmó su apuesta", apuesta)
                if oponente in self.juego:
                    respuesta["turno"] = jugador
                    respuesta["comando"] = "turno_listo"
                    bol_apostadas = self.juego[jugador][0]
                    if paridad(bol_apostadas) == self.juego[oponente][1]:
                        respuesta["ganador"] = oponente
                        bol_ganador = bol_apostadas + bolitas[1]
                        bol_perdedor = bolitas[0] - bol_apostadas
                        bolitas_nuevas = [bol_ganador, bol_perdedor]
                        respuesta["perdedor"] = jugador
                        respuesta["bolitas"] = bolitas_nuevas
                        respuesta["apuestas"] = [apuesta]
                        ap_oponente = self.juego[oponente][0]
                        aps = [ap_oponente, self.juego[oponente][1],
                              apuesta, paridad(apuesta)]
                        respuesta["apuestas"] = aps
                        logs(f"Partida entre {jugador} y {oponente}", "Ganador ronda", oponente)
                    else:
                        bol_apostadas = self.juego[oponente][0]
                        respuesta["ganador"] = jugador
                        bol_ganador = bolitas[0] + bol_apostadas 
                        bol_perdedor = bolitas[1] - bol_apostadas
                        bolitas_nuevas = [bol_ganador, bol_perdedor]
                        respuesta["perdedor"] = oponente
                        respuesta["bolitas"] = bolitas_nuevas
                        ap_oponente = self.juego[oponente][0]
                        aps = [apuesta, paridad(apuesta),
                              ap_oponente, self.juego[oponente][1]]
                        respuesta["apuestas"] = aps
                        logs(f"Partida entre {jugador} y {oponente}", "Ganador ronda", jugador)
                    socket_2 = self.clientes_conectados[oponente]
                    respuesta["socket"] = [self.clientes_conectados[jugador], socket_2]
                    del self.juego[jugador]
                    del self.juego[oponente]
                    for bolita in bolitas_nuevas:
                        if bolita >= 20:
                            respuesta["comando"] = "terminar_partida" 
                            del self.clientes_conectados[jugador]
                            del self.clientes_conectados[oponente]
                            logs("-", "Terminando partida", f"Ganador: {respuesta['ganador']}")
                            return respuesta
                    logs(jugador, "Comenzó su turno", "")
                else:
                    respuesta["comando"] = "turno_no_listo"
        elif comando == "volver_inicio":
            respuesta["comando"] = "mostrar_inicio"
        elif comando == "perder":
            respuesta["comando"] = "terminar_partida"
            respuesta["ganador"] = recibido["oponente"]
            respuesta["perdedor"] = recibido["jugador"]
            respuesta["socket"] = [self.clientes_conectados[recibido["oponente"]]]
            del self.clientes_conectados[recibido["oponente"]]
        elif comando == "salida":
            respuesta["comando"] = "salida"
        return respuesta
