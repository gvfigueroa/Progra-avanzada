from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from leer_archivo import leer_parametros

window_name, base_class = uic.loadUiType(leer_parametros("ventana_principal"))

class VentanaPrincipal(window_name, base_class):

    senal_enviar_login = pyqtSignal(tuple)
    senal_retar_jugador = pyqtSignal(int, str, str)
    senal_desconectarse = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_gui()
        self.usuario = ""
        self.usuarios = []
        #hago una lista de labels y de botones están en la pantalla de inicio por defecto
        #con su respectivo orden
        self.labels = [self.label_usuario_1,
                       self.label_usuario_2,
                       self.label_usuario_3,
                       self.label_usuario_4]
        self.buttons = [self.retar_button_1,
                        self.retar_button_2,
                        self.retar_button_3,
                        self.retar_button_4]

    def init_gui(self):
        self.setWindowTitle('Sala principal')

        #se conecta cada botón con el indice respectivo
        self.retar_button_1.clicked.connect(lambda: self.retar_jugador(0))
        self.retar_button_2.clicked.connect(lambda: self.retar_jugador(1))
        self.retar_button_3.clicked.connect(lambda: self.retar_jugador(2))
        self.retar_button_4.clicked.connect(lambda: self.retar_jugador(3))

        

    def mostrar(self, usuario, usuarios):
        #se muestran a los jugadores actuales en la ventana
        self.mostrar_jugadores(usuario, usuarios)
        self.show()

    #se envía el reto al usuario correspondiente al índice dado
    def retar_jugador(self, indice):
        retado = self.usuarios[indice]
        self.senal_retar_jugador.emit(indice, self.usuario, retado)
        self.buttons[indice].setEnabled(False)
        for i in range(len(self.buttons)):
            self.buttons[i].setEnabled(False)

    #se muestran los jugadores con sus respectivos botones,
    #en caso de no haber 4 se muestra que aún pueden entrar más
    #y el jugador no se puesde retar a si mismo
    def mostrar_jugadores(self, usuario, usuarios):
        self.usuario = usuario
        self.usuarios = usuarios
        jugadores = ""
        indice = 1
        for user in self.usuarios:
            jugadores = f"{indice}.  {user}\n" 
            self.labels[indice - 1].setText(jugadores)
            self.labels[indice - 1].setStyleSheet("color: white;"
                                                  "font: 12pt Segoe Print;")
            self.buttons[indice - 1].setEnabled(True)
            self.buttons[indice - 1].show()
            if user == self.usuario:
                self.buttons[indice - 1].hide()
            indice += 1
        if indice <= 4:
            self.labels[indice - 1].setStyleSheet("color: red;"
                                                  "font: 12pt Segoe Print;")
            self.labels[indice - 1].setText("Esperando jugador...")
            self.buttons[indice - 1].hide()
            indice += 1
            while indice <= 4:
                self.labels[indice - 1].setText("")
                self.buttons[indice - 1].hide()
                indice += 1

    def mostrar_nuevamente_jugadores(self, jugadores):
        #se actualizan los jugadores cada vez que entra o se va otro
        self.mostrar(self.usuario, jugadores)


    def actualizar_botones(self, usuario, indice):
        #actualizar botones cuandose reta a alguien
        indice_usuario = self.usuarios.index(usuario)
        self.buttons[indice_usuario].setEnabled(False)
        self.buttons[indice].setEnabled(False)


    def actualizar_jugadores(self, usuario, accion):
        #actualizar la lista de jugadores con el usuario dado
        #por el servidor y actualiza la pantalla
        if accion:
            self.usuarios.append(usuario)
        else:
            self.usuarios.remove(usuario)
        self.mostrar_jugadores(self.usuario, self.usuarios)

    def closeEvent(self, event):
        #se desconecta alusuario del servidor si es que cierra la 
        #ventana
        self.senal_desconectarse.emit(self.usuario)

    def ocultar(self):
        self.hide()


window_name, base_class = uic.loadUiType(leer_parametros("ventana_invitacion"))

class Invitacion(window_name, base_class):

    senal_respuesta_aceptar = pyqtSignal(str, str)
    senal_respuesta_rechazar = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.retador = ""
        self.retado = ""
        self.init_gui()
        
    def init_gui(self):
        self.setWindowTitle('Invitación')
        self.aceptar_button.clicked.connect(self.aceptar_reto)
        self.rechazar_button.clicked.connect(self.rechazar_reto)

    def mostrar_invitacion(self, usuario, yo):
        #muestra en el string quien te ha invitado a jugar
        self.retador = usuario
        self.retado = yo
        texto = f"{usuario} te ha invitado a jugar"
        self.label_user.setText(texto)
        self.show()

    def aceptar_reto(self):
        #si es que se acepta la invitacion
        self.senal_respuesta_aceptar.emit(self.retado, self.retador)

    def rechazar_reto(self):
        #si es que se rechaza
        self.senal_respuesta_rechazar.emit(self.retado, self.retador)

    def ocultar(self):
        self.hide()