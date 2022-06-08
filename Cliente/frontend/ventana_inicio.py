from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
from leer_archivo import leer_parametros

window_name, base_class = uic.loadUiType(leer_parametros("ventana_inicio"))

class VentanaInicio(window_name, base_class):

    senal_enviar_login = pyqtSignal(tuple)
    senal_mostrar_principal = pyqtSignal()
    senal_desconectarse =pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_gui()

    def init_gui(self):
        self.setWindowTitle('¡Hola!')
        self.ingresar_button.clicked.connect(self.enviar_login)
        self.show()
        
    def enviar_login(self):
        usuario = self.edit_nombre.text()
        fecha = self.edit_fecha.text()
        self.senal_enviar_login.emit((usuario, fecha))


    def recibir_validacion(self, booleano):
        if booleano:
            self.ocultar()
        else:
            self.pop_up()

    def pop_up(self):
        QMessageBox.about(self, "Error de conexión",
         f"No se ha podido establecer conexión con el servidor")

    def mostrar(self):
        self.show()

    def ocultar(self):
        self.hide()

    def closeEvent(self, event):
        self.senal_desconectarse.emit("")


