# Tarea X: Nombre de la tarea :school_satchel:


Un buen ```README.md``` puede marcar una gran diferencia en la facilidad con la que corregimos una tarea, y consecuentemente cómo funciona su programa, por lo en general, entre más ordenado y limpio sea éste, mejor será 

Para nuestra suerte, GitHub soporta el formato [MarkDown](https://es.wikipedia.org/wiki/Markdown), el cual permite utilizar una amplia variedad de estilos de texto, tanto para resaltar cosas importantes como para separar ideas o poner código de manera ordenada ([pueden ver casi todas las funcionalidades que incluye aquí](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet))

Un buen ```README.md``` no tiene por que ser muy extenso tampoco, hay que ser **concisos** (a menos que lo consideren necesario) pero **tampoco pueden** faltar cosas. Lo importante es que sea claro y limpio 

**Dejar claro lo que NO pudieron implementar y lo que no funciona a la perfección. Esto puede sonar innecesario pero permite que el ayudante se enfoque en lo que sí podría subir su puntaje.**

## Consideraciones generales :octocat:

<Descripción de lo que hace y que **_no_** hace la tarea que entregaron junto
con detalles de último minuto y consideraciones como por ejemplo cambiar algo
en cierta línea del código o comentar una función>

### Cosas implementadas y no implementadas :white_check_mark: :x:

Explicación: mantén el emoji correspondiente, de manera honesta, para cada item. Si quieres, también puedes agregarlos a los títulos:
- ❌ si **NO** completaste lo pedido
- ✅ si completaste **correctamente** lo pedido
- 🟠 si el item está **incompleto** o tiene algunos errores
#### Networking: 23 pts (18%)
##### ✅ Protocolo <explicacion\>
##### ✅ Correcto uso de sockets <explicacion\>
##### ✅ Conexión <explicacion\>
##### ✅ Manejo de clientes <explicacion\>
#### Arquitectura Cliente - Servidor: 31 pts (24%)
##### ✅ Roles <explicacion\>
##### ✅ Consistencia <explicacion\>
##### ✅ Logs <explicacion\>
#### Manejo de Bytes: 20 pts (15%)
##### ✅ Codificación <explicacion\>
##### ✅ Decodificación <explicacion\>
##### ✅ Encriptación <explicacion\>
##### ✅ Integración <explicacion\>
#### Interfaz gráfica: 31 pts (24%)
##### ✅ Modelación <explicacion\>
##### ✅ Ventana inicio <explicacion\>
##### ✅ Sala Principal <explicacion\>
##### ✅ Ventana de Invitación <explicacion\>
##### ✅ Sala de juego <explicacion\>
##### ✅ Ventana final <explicacion\>
#### Reglas de DCCalamar: 21 pts (16%)
##### ✅ Inicio del juego <explicacion\>
##### ✅ Ronda <explicacion\>
##### ✅ Termino del juego <explicacion\>
#### General: 4 pts (3%)
##### ✅ Parámetros (JSON) <explicacion\>
#### Bonus: 5 décimas máximo
##### ❌ Cheatcode <explicacion\>
##### ❌ Turnos con tiempo <explicacion\>
## Ejecución :computer:
El módulo principal de la tarea a ejecutar es  ```main.py``` tanto para el servidor como para el cliente. y no es necesario crear nada extra aparte de los sprites **Que debe estar dentro de servidor/frontend**


## Librerías :books:
### Librerías externas utilizadas
La lista de librerías externas que utilicé fue la siguiente:

1. ```PyQt5```: ```uic```
2. ```PyQt5.QtCore```: ```pyqtSignal, QObject, QEventLoop, QTimer``` 
3. ```PyQt5.QtGui```: ```QPixmap```
4. ```PyQt5.QtWidgets```: ```QMessageBox, QLabel, QButtonGroup```
5. ```random```: ```randint, choice```
6. ```os```: ```path.join```
7. ```json```: ```dump```, ```loads```
8. ```socket```: ```socket```, ```AF_INET```,  ```SOCK_STREAM```,```connect```,```recv```
9. ```threading```: ```Thread```, ```lock```
10. ```sys```: ```exit```



### Librerías propias
Por otro lado, los módulos que fueron creados fueron los siguientes:

1. ```cliente.cliente```: Contiene a ```Cliente```, que funciona como el procesador del cliente
2. ```servidor.servidor```: Contiene a ```Servidor```, que funciona como el servidor
3. ```servidor.complementos```: Contiene funicones complementarias a la clase servidor
4. ```leer_archivo```: Contiene a la funcion leer parametros que lee la información de parametros.json
5. ```parametros.json```: parametros, uno para el cliente y otro para el servidor
6. ```cliente.frontend.ventana_inicio```: Contiene a ```VentanaInicio```, que es el frontend de la ventana incial
7. ```cliente.frontend.ventana_principal```: Contiene a ```VentanaPrincipal```, ```VentanaInvitacion```, que son el frontend de las ventanas principal y de invitacion
8. ```cliente.frontend.ventana_juego```: Contiene a ```VentanaJuego```, ```VentanaFinal```, que son el frontend de las ventanas juego y final

## Supuestos y consideraciones adicionales :thinking:
Los supuestos que realicé durante la tarea son los siguientes:

1. Durante una partida, la pantalla tendrá el mensaje por defecto de "esperando..." y esperando a jugador y no escutualizará hasta que ambos jugadores envíen su apuesta 
2. Luego de que ambos jugadores envíen su apuesta, se muestran durante 2 segundos los resultados en pantalla y luego se actualiza la ventana para el siguiente turno
3. Cuando un jugador gana, no se muestran los resultados en ventana y pasa directamente a la pantalla final
4. Si no se cumplen los requisitos para entrar a la ventana principal se muestra el mensaje "No se ha podido establecer conexión con el servidor" independientemente de la razón (usuario/fecha inválidos o sala llena)



Lo importante es que expliquen qué hace la función y que si saben que alguna parte puede quedar complicada de entender o tienen alguna función mágica usen los comentarios/documentación para que el ayudante entienda sus intenciones.

## Referencias de código externo :book:

Para realizar mi tarea saqué código de:
1. \<https://stackoverflow.com/questions/26293638/how-to-allow-only-one-checkbox-checked-at-a-time: este permite que se pueda marcar sólo una check box: línea 29-31 en ventana_juego
2.\<https://stackoverflow.com/questions/48039309/time-sleep-and-background-windows-pyqt5: equivalente a sleep en qt para poder mostrar los resultados en pantalla antes de pasar turno: línea 160-162 en ventana_juego
3. Código general de la AF4
