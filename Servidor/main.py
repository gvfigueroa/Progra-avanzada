import sys
from servidor import Servidor

from leer_archivo import leer_parametros

    
if __name__ == "__main__":
    
    HOST = leer_parametros("host")  # "localhost"
    PORT = leer_parametros("port")
    servidor = Servidor(HOST, PORT)

    try:
        input("")
    except KeyboardInterrupt:
        print("Cerrando servidor...")
        servidor.socket_servidor.close()
        sys.exit()
