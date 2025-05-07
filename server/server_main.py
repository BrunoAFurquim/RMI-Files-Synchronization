from http.server import HTTPServer
from server.dispatcher import RequestDispatcher
import logging
from server.file_handler import FileHandler
import socket

class MyHTTPServer(HTTPServer):
    """Classe customizada para melhor controle do servidor HTTP"""
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.request_queue_size = 20
        self.timeout = 60 
        self.max_packet_size = 8192 

def run_server():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('server.log'),
            logging.StreamHandler()
        ]
    )

    try:
        FileHandler.initialize()
        logging.info("Arquivos do servidor inicializados com sucesso")
    except Exception as e:
        logging.critical(f"Falha na inicialização: {e}")
        return

    server_address = ('localhost', 8000)
    
    try:
        httpd = MyHTTPServer(server_address, RequestDispatcher)
        # Configuração adicional do socket
        httpd.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        logging.info(f"Servidor RMI rodando em http://{server_address[0]}:{server_address[1]}")
        logging.info("Pressione Ctrl+C para encerrar...")

        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("\nEncerrando servidor graciosamente...")
    except Exception as e:
        logging.critical(f"Erro fatal no servidor: {e}")
    finally:
        httpd.server_close()
        logging.info("Servidor encerrado")

if __name__ == '__main__':
    run_server()