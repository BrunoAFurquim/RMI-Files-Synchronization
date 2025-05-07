from datetime import datetime
from http.server import BaseHTTPRequestHandler
import json
import threading
import logging
from common.auth import authenticate
from server.file_handler import FileHandler
from server.threads import RequestThread

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dispatcher.log'),
        logging.StreamHandler()
    ]
)

class RequestDispatcher(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, extra_headers=None):
        """Configura os cabeçalhos HTTP de resposta"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Connection', 'keep-alive')
        
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
                
        self.end_headers()
    
    def do_POST(self):
        """Processa requisições POST"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                raise ValueError("Content-Length inválido")
                
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data)
            except json.JSONDecodeError as je:
                logging.error(f"JSON inválido: {str(je)}")
                self._set_headers(400)
                response = {
                    'status': 'error',
                    'code': 'INVALID_JSON',
                    'message': 'Formato JSON inválido'
                }
                self.wfile.write(json.dumps(response).encode())
                return
                
            # Log da requisição recebida
            logging.info(f"Requisição recebida: {request_data.get('method')}")
            
            # Processa em uma thread separada
            thread = RequestThread(self, request_data)
            thread.start()
            
        except Exception as e:
            logging.error(f"Erro ao processar requisição: {str(e)}", exc_info=True)
            self._set_headers(500)
            response = {
                'status': 'error',
                'code': 'SERVER_ERROR',
                'message': 'Erro interno no servidor'
            }
            self.wfile.write(json.dumps(response).encode())

    def handle_request(self, request_data):
        """Manipula a requisição e retorna a resposta"""
        try:
            # Configurações de conexão
            self.protocol_version = 'HTTP/1.1'
            self.close_connection = False
            
            # 1. Autenticação
            auth_token = request_data.get('auth_token')
            if not authenticate(auth_token):
                logging.warning(f"Autenticação falhou para token: {auth_token[:8]}...")
                self._set_headers(401)
                return {
                    'status': 'error',
                    'code': 'UNAUTHORIZED',
                    'message': 'Credenciais inválidas'
                }

            # 2. Validação do método
            method_name = request_data.get('method')
            if not method_name:
                logging.warning("Requisição sem método")
                self._set_headers(400)
                return {
                    'status': 'error',
                    'code': 'METHOD_REQUIRED',
                    'message': 'Parâmetro "method" é obrigatório'
                }

            # 3. Roteamento para handlers
            handlers = {
                'get_file_content': self._handle_get_content,
                'check_master_version': self._handle_check_version,
                'synchronize': self._handle_sync,
                'confirm_sync': self._handle_confirm_sync,
                'update_master_file': self._handle_update_file
            }

            handler = handlers.get(method_name)
            if not handler:
                logging.warning(f"Método não encontrado: {method_name}")
                self._set_headers(404)
                return {
                    'status': 'error',
                    'code': 'METHOD_NOT_FOUND',
                    'message': f'Método {method_name} não existe'
                }

            # 4. Execução do handler
            response = handler(request_data)
            
            # 5. Envio da resposta
            response_data = json.dumps(response).encode('utf-8')
            self._set_headers(extra_headers={
                'Content-Length': str(len(response_data))
            })
            self.wfile.write(response_data)
            
            return response

        except Exception as e:
            logging.error(f"Erro no handle_request: {str(e)}", exc_info=True)
            self._set_headers(500)
            return {
                'status': 'error',
                'code': 'INTERNAL_ERROR',
                'message': str(e)
            }

    # Handlers específicos
    def _handle_get_content(self, request_data):
        """Handler para obter conteúdo do arquivo"""
        try:
            content = FileHandler.get_content()
            version = FileHandler.get_version()
            
            if content is None:
                raise ValueError("Conteúdo do arquivo não disponível")
                
            return {
                'status': 'success',
                'content': content,
                'version': version,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Erro no _handle_get_content: {str(e)}")
            raise

    def _handle_check_version(self, request_data):
        """Handler para verificar versão do arquivo"""
        try:
            version = FileHandler.get_version()
            
            if version in ["error", "empty_file"]:
                raise RuntimeError(f"Erro ao obter versão: {version}")
                
            return {
                'status': 'success',
                'version': version,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Erro no _handle_check_version: {str(e)}")
            raise

    def _handle_sync(self, request_data):
        """Handler para sincronização"""
        try:
            mode = request_data.get('mode', 'R')
            auth_token = request_data.get('auth_token')
            
            FileHandler.log_sync(auth_token, mode)
            
            return {
                'status': 'success',
                'mode': mode,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Erro no _handle_sync: {str(e)}")
            raise

    def _handle_confirm_sync(self, request_data):
        """Handler para confirmação de sincronização"""
        try:
            protocol = request_data.get('protocol')
            auth_token = request_data.get('auth_token')
            
            if protocol not in ['RR', 'RRA']:
                raise ValueError("Protocolo inválido")
                
            FileHandler.log_sync(auth_token, protocol)
            
            return {
                'status': 'success',
                'protocol': protocol,
                'confirmed_at': datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Erro no _handle_confirm_sync: {str(e)}")
            raise

    def _handle_update_file(self, request_data):
        """Handler para atualização do arquivo master"""
        try:
            auth_token = request_data.get('auth_token')
            new_content = request_data.get('new_content')
            
            if not authenticate(auth_token, admin=True):
                raise PermissionError("Acesso administrativo requerido")
                
            if not isinstance(new_content, str):
                raise TypeError("Conteúdo deve ser uma string")
                
            success = FileHandler.update_content(new_content)
            
            return {
                'status': 'success' if success else 'error',
                'updated_at': datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"Erro no _handle_update_file: {str(e)}")
            raise