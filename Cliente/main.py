import socket
from PyQt5.QtWidgets import QApplication
from backend.cliente import Cliente
from frontend.ventana_inicio import VentanaInicio
from frontend.ventana_principal import VentanaPrincipal, Invitacion
from frontend.ventana_juego import VentanaJuego, VentanaFinal
from leer_archivo import leer_parametros


if __name__ == "__main__":
    HOST = leer_parametros("host")  # "localhost"
    PORT = leer_parametros("port")

    app = QApplication([])
    ventana_inicio = VentanaInicio()
    CLIENTE = Cliente(HOST, PORT)
    ventana_principal = VentanaPrincipal()
    ventana_invitacion = Invitacion()
    ventana_juego = VentanaJuego()
    ventana_final = VentanaFinal()

    #ingreso de usuario y su validación
    ventana_inicio.senal_enviar_login.connect(CLIENTE.enviar_ingreso)
    CLIENTE.senal_respuesta_validacion.connect(ventana_inicio.recibir_validacion)
    CLIENTE.senal_mostrar_principal.connect(ventana_principal.mostrar)

    #actualizar jugadores en ventana cada vez que alguien ingresa o alguien se va
    CLIENTE.senal_actualizar_jugadores.connect(ventana_principal.actualizar_jugadores)

    #retar jugador, mostrar su respectiva invitacion y modificar botones de ventana principal
    ventana_principal.senal_retar_jugador.connect(CLIENTE.retar_jugador)
    CLIENTE.senal_invitacion.connect(ventana_invitacion.mostrar_invitacion)
    CLIENTE.senal_actualizar_botones.connect(ventana_principal.actualizar_botones)
    CLIENTE.senal_ocultar_principal.connect(ventana_principal.ocultar)

    #senal de aceptar o rechazar reto
    ventana_invitacion.senal_respuesta_aceptar.connect(CLIENTE.aceptar_reto)
    ventana_invitacion.senal_respuesta_rechazar.connect(CLIENTE.rechazar_reto)

    #si se acepta
    CLIENTE.senal_comenzar_juego.connect(ventana_juego.mostrar)
    CLIENTE.senal_ocultar_invitacion.connect(ventana_invitacion.ocultar)

    #si se rechaza
    CLIENTE.senal_reiniciar_principal.connect(ventana_principal.mostrar_nuevamente_jugadores)



    #señales para avanzar el juego 
    ventana_juego.senal_enviar_apuesta.connect(CLIENTE.enviar_apuesta)
    CLIENTE.senal_avanzar_juego.connect(ventana_juego.avanzar_juego)

    #señales para conectar ventanas luego de ganar
    CLIENTE.senal_terminar_juego.connect(ventana_final.mostrar)
    CLIENTE.senal_ocultar_juego.connect(ventana_juego.ocultar)

    #si se elige jugar de nuevo
    ventana_final.senal_volver_inicio.connect(CLIENTE.volver_inicio)
    CLIENTE.senal_mostrar_inicio.connect(ventana_inicio.mostrar)

    #señales al cerrar ventanas
    ventana_principal.senal_desconectarse.connect(CLIENTE.salir)
    ventana_juego.senal_desconectarse.connect(CLIENTE.salir_juego)
    CLIENTE.senal_ocultar_inicio.connect(ventana_inicio.ocultar)
    ventana_juego.senal_perder.connect(CLIENTE.perder)
    ventana_inicio.senal_desconectarse.connect(CLIENTE.salida)


    
    app.exec()