from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal, QEventLoop, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMessageBox, QLabel, QButtonGroup
from leer_archivo import leer_parametros


window_name, base_class = uic.loadUiType(leer_parametros("ventana_juego"))

class VentanaJuego(window_name, base_class):

    senal_enviar_apuesta = pyqtSignal(int, str, list, list, str)
    senal_desconectarse = pyqtSignal(str)
    senal_perder = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.en_turno = False
        self.bolitas_de_1 = 10
        self.bolitas_de_2 = 10
        self.jugador = ""
        self.oponente = ""
        self.init_gui()

    def init_gui(self):
        self.setWindowTitle('¡A jugar!')
        self.listo_button.clicked.connect(self.enviar_apuesta)
        self.group = QButtonGroup(self)
        self.group.addButton(self.checkBox_2)
        self.group.addButton(self.checkBox)
        self.spinBox.setMinimum(1)


    
    def enviar_apuesta(self):
        apuesta = self.spinBox.value()
        impar = self.checkBox_2.isChecked()
        par = self.checkBox.isChecked()
        #dependiendo de si es mi turno o no envio mi apuesta del oponente
        if self.en_turno:
            if par:
                apuesta_oponente = "par"
            elif impar:
                apuesta_oponente = "impar"
        else:
            apuesta_oponente = "no_en_turno"
        jugadores = [self.jugador, self.oponente]
        bolitas = [self.bolitas_de_1, self.bolitas_de_2]
        self.senal_enviar_apuesta.emit(apuesta, apuesta_oponente, jugadores, bolitas, self.le_toca)

        
    def asignar_turnos(self, yo, jugador, jugadores, avatar):
        #recibo la info del servidor sobre a quien le toca 
        #y cual avatar para iniciar la ventana juego
        #Defino jugador en turno, jugador actual y oponente
        self.le_toca = jugador
        self.jugador = yo
        for jug in jugadores:
            if jug != self.jugador:
                self.oponente = jug
        #defino las posibles posiciones de los avatar 
        x_1 = leer_parametros("x_1")
        x_2 = leer_parametros("x_2")
        y_1 = leer_parametros("y_1")
        y_2 = leer_parametros("y_2")
        #escribo las bolitas de cada jugador en la ventana y su nombre
        self.bolitas_1.setText(str(self.bolitas_de_1))
        self.jugador_1.setText(f"Jugador: {self.jugador}")
        self.bolitas_2.setText(str(self.bolitas_de_2))
        self.jugador_2.setText(f"Jugador: {self.oponente}")
        #se escriben los textos de la ventana dependiendo 
        #de si está en turno o no y se mueven los avatar
        if self.jugador == jugador:
            self.label_1.setText("¿Cuántas canicas apuesta?")
            self.label_2.setText("La apuesta de tu oponente es")
            self.label_3.setText("¿Cuál es su apuesta?")
            self.label_4.setText("El valor de tu apuesta es")
            self.en_turno = True
            if avatar == 1:
                pass
            else:
                self.imagen_2.move(x_1, y_1)
                self.imagen_1.move(x_2, y_2)
        else:
            self.label_1.setText("¿Cuál es su apuesta?")
            self.label_2.setText("El valor de tu apuesta es")
            self.label_3.setText("¿Cuántas canicas apuesta?")
            self.label_4.setText("La apuesta de tu oponente es")
            self.checkBox.setEnabled(False)
            self.checkBox.hide()
            self.checkBox_2.hide()
            self.checkBox_2.setEnabled(False)
            if avatar == 2:
                pass
            else:
                self.imagen_2.move(x_1, y_1)
                self.imagen_1.move(x_2, y_2)
        #se escribe la parte por defecto de cada ventana
        self.label_5.setText("Esperando...")
        self.label_6.setText("Esperando...")
        self.label_resultado.setText(f"Esperando a {self.oponente}")
        #se define el máximo de la spinbox como el número de bolitas del jugador
        self.spinBox.setMaximum(self.bolitas_de_1)

    #se muestra la ventana con todos los datos dados arriba
    def mostrar(self, identificador, jugadores, turno, avatar):
        self.asignar_turnos(identificador, jugadores, turno, avatar)
        self.show()


    def avanzar_juego(self, ganador, perdedor, bolitas, apuestas, turno):
        #una vez que el servidor procesó 
        #las apuestas, llega la información a esta función
        #se modifican los textos de resultados en la pantalla
        #si el jugador en pantalla es el ganador:
        if self.jugador == ganador:
            self.label_resultado.setText(f"{perdedor} ha perdido!\n"
                                         f"Ganas {bolitas[0] - self.bolitas_de_1} "
                                         f"canicas")
            self.label_5.setText(f"{apuestas[2]}")
            self.label_6.setText(f"{apuestas[3]}")
            self.imagen_resultado.hide()
            self.bolitas_de_1 = bolitas[0]
            self.bolitas_1.setText(str(self.bolitas_de_1))
            self.bolitas_de_2 = bolitas[1]
            self.bolitas_2.setText(str(self.bolitas_de_2))
            if not self.en_turno:
                if apuestas[1] == "par":
                    self.checkBox.setEnabled(False)
                    self.checkBox.show()
                    self.checkBox.setChecked(True)
                else:
                    self.checkBox_2.show()
                    self.checkBox_2.setEnabled(False)
                    self.checkBox.setChecked(True)
        #si el jugador en pantalla es el perdedor:   
        else:
            self.label_resultado.setText(f"Has perdido!\n"
                                         f"Pierdes {self.bolitas_de_1 - bolitas[1]} "
                                         f"canicas")
            self.label_5.setText(f"{apuestas[0]}")
            self.label_6.setText(f"{apuestas[1]}")
            self.imagen_resultado.hide()
            self.bolitas_de_1 = bolitas[1]
            self.bolitas_1.setText(str(self.bolitas_de_1))
            self.bolitas_de_2 = bolitas[0]
            self.bolitas_2.setText(str(self.bolitas_de_2))
            if not self.en_turno:
                if apuestas[3] == "par":
                    self.checkBox.setEnabled(False)
                    self.checkBox.show()
                    self.checkBox.setChecked(True)
                else:
                    self.checkBox_2.show()
                    self.checkBox_2.setEnabled(False)
                    self.checkBox_2.setChecked(True)
        #se espera un tiempo de 2 segundos para mostrar 
        #los resultados del turno y luego se pasa al siguiente
        loop = QEventLoop()
        QTimer.singleShot(2000, loop.quit)
        loop.exec_()
        self.spinBox.setValue(0)
        #se revisa el turno enviado por el servido para definir 
        #una variable que me permite saber si me encuentro en un turno
        if self.jugador == turno:
            self.en_turno = True
        else:
            self.en_turno = False
        #se redefine el maximo del spin box como la nueva
        # cantidad de bolitas del jugador
        self.spinBox.setMaximum(self.bolitas_de_1)
        #se reescribe toda la pantalla de juego 
        self.set_labels_turnos()


    def set_labels_turnos(self):
        #se cambian los strings y checkboxs de la pantalla dependiendo del turno
        if self.en_turno:
            self.label_1.setText("¿Cuántas canicas apuesta?")
            self.label_2.setText("La apuesta de tu oponente es")
            self.label_3.setText("¿Cuál es su apuesta?")
            self.label_4.setText("El valor de tu apuesta es")
            self.checkBox.setEnabled(True)
            self.checkBox.show()
            self.checkBox_2.show()
            self.checkBox_2.setEnabled(True)
            self.checkBox.setChecked(False)
            self.checkBox_2.setChecked(False)

        else:
            self.label_1.setText("¿Cuál es su apuesta?")
            self.label_2.setText("El valor de tu apuesta es")
            self.label_3.setText("¿Cuántas canicas apuesta?")
            self.label_4.setText("La apuesta de tu oponente es")
            self.checkBox.setEnabled(False)
            self.checkBox.hide()
            self.checkBox_2.hide()
            self.checkBox_2.setEnabled(False)
            self.checkBox.setChecked(False)
            self.checkBox_2.setChecked(False)
        self.label_5.setText("Esperando...")
        self.label_6.setText("Esperando...")
        self.label_resultado.setText(f"Esperando a {self.oponente}")
        self.imagen_resultado.show()

    def ocultar(self):
        #se deja la pantalla como estaba inicialmente cada elemneto y se oculta la pantalla
        self.checkBox.setEnabled(True)
        self.checkBox_2.setEnabled(True)
        self.checkBox.setChecked(False)
        self.checkBox_2.setChecked(False)
        self.checkBox.show()
        self.checkBox_2.show()
        self.en_turno = False
        self.spinBox.setValue(0)
        self.bolitas_de_1 = 10
        self.bolitas_de_2 = 10
        x_1 = leer_parametros("x_1")
        x_2 = leer_parametros("x_2")
        y_1 = leer_parametros("y_1")
        y_2 = leer_parametros("y_2")
        self.imagen_2.move(x_2, y_2)
        self.imagen_1.move(x_1, y_1)
        self.hide()

    def closeEvent(self, event):
        #en caso de cerrar esta ventana, se declara ganador al oponente
        self.senal_perder.emit(self.jugador, self.oponente)
        self.senal_desconectarse.emit(self.jugador)


window_name, base_class = uic.loadUiType(leer_parametros("ventana_final"))

class VentanaFinal (window_name, base_class):

    senal_volver_inicio = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_gui()

    def init_gui(self):
        self.setWindowTitle('Fin del DCCalamar')
        #se conecta el boton para volver al inicio
        self.de_nuevo_button.clicked.connect(self.volver_inicio)

    def mostrar(self, ganador, perdedor):
        #se muesta al ganador y perdedor luego de pasar por el servidor
        self.label_ganador.setText(f"{ganador}")
        self.label_perdedor.setText(f"{perdedor}")
        self.show()

    def ocultar(self):
        self.hide()

    def volver_inicio(self):
        #senal para avisar al servido de que se quiere volver al inicio
        self.senal_volver_inicio.emit()
        self.ocultar()