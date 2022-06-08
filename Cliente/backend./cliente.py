from PyQt5.QtCore import QObject, pyqtSignal
import json
import socket
import threading
import sys
from leer_archivo import leer_parametros

#import menus


class Cliente(QObject):
    senal_respuesta_validacion = pyqtSignal(bool)
    senal_mostrar_principal = pyqtSignal(str, list)
    senal_actualizar_jugadores = pyqtSignal(str, bool)
    senal_invitacion = pyqtSignal(str, str)
    senal_actualizar_botones = pyqtSignal(str, int)
    senal_ocultar_principal = pyqtSignal()
    senal_comenzar_juego = pyqtSignal(str, str, list, int)
    senal_reiniciar_principal = pyqtSignal(list)
    senal_ocultar_invitacion = pyqtSignal()
    senal_avanzar_juego = pyqtSignal(str, str, list, list, str)
    senal_terminar_juego = pyqtSignal(str, str)
    senal_ocultar_juego = pyqtSignal()
    senal_mostrar_inicio = pyqtSignal()
    senal_ocultar_inicio = pyqtSignal()
    def __init__(self, host, port):
        
        super().__init__()
        self.host = host
        self.port = port
        self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.jugadores = []
        self.usuario = ""

        try:
            #se conecta al servidor y procesa errores en caso de haberlos
            self.conectar_al_servidor()
            self.escuchar()
        except ConnectionError:
            self.salir(self.usuario)
        except ConnectionResetError:
            self.salir(self.usuario)

    def conectar_al_servidor(self):
        self.socket_cliente.connect((self.host, self.port))
        print("El cliente se ha conectado exitosamente al servidor")

    def escuchar(self):
        thread = threading.Thread(target=self.thread_escuchar)
        thread.start()

    def thread_escuchar(self):
        while True:
            try:
                #procesa los mensajes para leerlos usando el 
                #metodo de desencriptación
                condicion = bytearray()
                response_bytes_length = self.socket_cliente.recv(4)
                response_length = int.from_bytes(
                    response_bytes_length, byteorder='little')
                response = bytearray()
                basura = bytearray()
                indice = 0
                TAMANO_CHUNK = leer_parametros("tamano_chunk")
                while len(response) < response_length:
                    numero_chunk = self.socket_cliente.recv(4)
                    orden = int.from_bytes(numero_chunk, byteorder='big')
                    read_length = min(TAMANO_CHUNK, response_length - len(response))
                    indice += read_length
                    response.extend(self.socket_cliente.recv(read_length))
                    if read_length != TAMANO_CHUNK:
                        basura.extend(self.socket_cliente.recv(TAMANO_CHUNK - read_length))
                condicion = response[indice - 1 : indice]
                response = response[:-1]
                mensaje_desencriptado = self.desencriptar_mensaje(response, condicion)
                received = self.decodificar_mensaje(mensaje_desencriptado)
                self.manejar_comando(received)
            except ConnectionAbortedError:
                self.salir(self.usuario)
                break
            except ConnectionResetError:
                self.salir(self.usuario)
                break


    #metodo de encripatación
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
    #método de desencripatación
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

    #método para enviar la información usando el método de
    #encriptación
    def enviar(self, msg):
        try:
            mensaje_codificado = self.codificar_mensaje(msg)
            mensaje_encriptado = self.encriptar_mensaje(mensaje_codificado)
            largo_mensaje = len(mensaje_encriptado).to_bytes(4, byteorder='little')
            TAMANO_CHUNK = leer_parametros("tamano_chunk")
            numero_de_bloque = 0
            self.socket_cliente.send(largo_mensaje)
            for i in range(0, len(mensaje_encriptado), TAMANO_CHUNK):
                chunk = bytearray(mensaje_encriptado[i : i + TAMANO_CHUNK])
                while len(chunk) < TAMANO_CHUNK:
                    chunk.extend(bytearray(b"\x00"))
                numero_chunk = numero_de_bloque.to_bytes(4, byteorder='big')
                self.socket_cliente.send(numero_chunk + bytes(chunk))
                numero_de_bloque += 1
        except ConnectionResetError:
            self.senal_ocultar_principal.emit()
            self.senal_ocultar_inicio.emit()
            self.senal_ocultar_invitacion.emit()
            self.senal_ocultar_juego.emit()
            self.socket_cliente.close()
            exit()


    #envía la información de ingreso (nombre y fecha)
    def enviar_ingreso(self, data):
        self.enviar({
            "comando": "ingreso",
            "usuario": str(data[0]),
            "fecha": str(data[1])
            })
        self.usuario = data[0]

 
    #codifica el mensaje
    @staticmethod
    def codificar_mensaje(mensaje):
        try:
            mensaje_json = json.dumps(mensaje)
            mensaje_bytes = mensaje_json.encode("UTF-8")
            return mensaje_bytes
        except json.JSONDecodeError:
            print('No se pudo codificar el mensaje.')

    #decodifica el mensaje
    @staticmethod
    def decodificar_mensaje(msg_bytes):
        try:
            mensaje = json.loads(msg_bytes)
            return mensaje
        except json.JSONDecodeError:
            print('No se pudo decodificar el mensaje.')
            return dict()

    def recibir_input(self):
        thread = threading.Thread(target=self.thread_recibir_input, daemon=True)
        thread.start()

    #encargado de catalogar los mensajes entrantes
    def manejar_comando(self, recibido):
        comando = recibido.get("comando")
        if comando == "ingreso":
            #si el pase es afirmativo, muestra la ventana principal y sus usuarios
            if recibido["pase"]:
                self.senal_respuesta_validacion.emit(True)
                self.senal_mostrar_principal.emit(recibido["usuario"], recibido["usuarios"])
                self.jugadores = recibido["usuarios"]
            else:
                #si el pase es negativo, avisa a la ventana de validación que muestra un popup
                self.senal_respuesta_validacion.emit(False)
        elif comando == "actualizar_sala_principal":
            #Actualiza ventana principal, ya sea agregando a un usuario o sacándolo
            if recibido["pase"]:
                self.senal_actualizar_jugadores.emit(recibido["usuario"], True)
            else:
                self.senal_actualizar_jugadores.emit(recibido["usuario"], False)
            self.jugadores = recibido["usuarios"]
        elif comando == "reto":
            #envía el reto
            self.senal_invitacion.emit(recibido["usuario"], recibido["retado"])
            self.senal_ocultar_principal.emit()
        elif comando == "actualizar_botones":
            #actualiza botones mientras hay jugadores esperando respuesta de retos
            self.senal_actualizar_botones.emit(recibido["usuario"], recibido["indice"])
        elif comando == "comenzar_juego":
            #Si la respuesta del reto fue positiva se comienza el juego con la información
            #entregada por el servidor
            turno = recibido["turno"]
            jugadores = [recibido["retado"], recibido["retador"]]
            yo = recibido["soy"]
            self.senal_comenzar_juego.emit(yo, turno, jugadores, recibido["avatar"])
            self.senal_ocultar_principal.emit()
            self.senal_ocultar_invitacion.emit()
        elif comando == "volver_sala_principal":
            #Si no se acepta el reto, sse vuelve a la pantalla principal
            self.senal_reiniciar_principal.emit(recibido["usuarios"])
            self.senal_ocultar_invitacion.emit()
        elif comando == "nada":
            #cuando la respuesta recibida es útil sólo para quien la envió,
            #el resto de usuario no hace nada
            pass
        elif comando == "turno_listo":
            #llega cuando ambos jugadores enviaron su apuesta
            ganador = recibido["ganador"]
            perdedor = recibido["perdedor"]
            self.senal_avanzar_juego.emit(ganador, perdedor,
                                         recibido["bolitas"], recibido["apuestas"],
                                         recibido["turno"])
        elif comando == "terminar_partida":
            #cuando un jugador gana
            ganador = recibido["ganador"]
            perdedor = recibido["perdedor"]
            self.senal_terminar_juego.emit(ganador, perdedor)
            self.senal_ocultar_juego.emit()
        elif comando == "mostrar_inicio":
            #si es que luego de ganar, el jugador quiere volver al inicio
            self.senal_mostrar_inicio.emit()
        elif comando == "desconexion_server":
            #lo que hace en caso de que el server se desconecte repentinamente
            print("El servidor se ha desconectado")
            self.senal_ocultar_principal.emit()
            self.senal_ocultar_inicio.emit()
            self.senal_ocultar_invitacion.emit()
            self.senal_ocultar_juego.emit()
            self.socket_cliente.close()
            sys.exit()
        elif comando == "salir" or comando == "salir_juego":
            #si se cierra alguna ventana
            self.socket_cliente.close()
            exit()
        elif comando == "desconectar_terminal":
            #para no dejar la terminal pegada
            self.socket_cliente.close()
            exit()

    #enviar la salida del usuario de la ventana principal
    def salir(self, usuario):
        self.enviar({
            "comando": "salir",
            "usuario": usuario
            })

    #enviar la salida del usuario de la ventana juego
    def salir_juego(self, usuario):
        self.enviar({
            "comando": "salir_juego",
            "usuario": usuario
            })

    #enviar el reto al jugador
    def retar_jugador(self, indice, usuario, retado):
        self.enviar({
            "comando": "retar",
            "usuario": self.usuario,
            "retado": retado,
            "indice": indice
            })
    #aceptar reto de jugador
    def aceptar_reto(self, retado, retador):
        self.enviar({
            "comando": "aceptar_reto",
            "retado": retado,
            "retador": retador
            })

    #rechazar reto de jugador
    def rechazar_reto(self, retado, retador):
        self.enviar({
            "comando": "rechazar_reto",
            "retado": retado,
            "retador": retador
            })

    #enviar apuesta durante el juego
    def enviar_apuesta(self, apuesta, apuesta_oponente, jugadores, bolitas, en_turno):
        self.enviar({
            "comando": "apuesta",
            "apuesta": apuesta,
            "apuesta_oponente": apuesta_oponente,
            "jugadores": jugadores,
            "bolitas": bolitas,
            "turno": en_turno
            })

    #volver al inicio
    def volver_inicio(self):
        self.enviar({
            "comando": "volver_inicio"
            })
    #perder al cerrar la pantalla de juego
    def perder(self, jugador, oponente):
        self.enviar({
            "comando": "perder",
            "jugador": jugador,
            "oponente": oponente
            })

    #para no dejar pegada la terminal
    def salida(self):
        self.enviar({
            "comando": "salida"
            })