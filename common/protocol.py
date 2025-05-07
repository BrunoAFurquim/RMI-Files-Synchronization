from enum import Enum
import logging
from typing import Callable, Optional
from functools import wraps
import time

class SyncProtocol(Enum):
    """Enumeração dos protocolos de sincronização disponíveis"""
    R = "Simple Request"
    RR = "Request-Response"
    RRA = "Request-Response with Async Acknowledgment"

def log_protocol_usage(func: Callable):
    """Decorator para logar o uso dos protocolos"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        protocol = kwargs.get('protocol', SyncProtocol.R)
        start_time = time.time()
        
        logging.info(f"Iniciando operação com protocolo {protocol.name} - {protocol.value}")
        result = func(*args, **kwargs)
        
        duration = time.time() - start_time
        logging.info(f"Operação {protocol.name} concluída em {duration:.2f}s")
        
        return result
    return wrapper

class ProtocolHandler:
    def __init__(self, stub):
        """Inicializa o handler com um stub para comunicação remota"""
        self.stub = stub
        self.pending_acknowledgments = set()
    
    @log_protocol_usage
    def sync_file(self, protocol: SyncProtocol = SyncProtocol.R) -> bool:
        """
        Executa a sincronização usando o protocolo especificado
        Retorna True se a sincronização foi bem-sucedida
        """
        if protocol == SyncProtocol.R:
            return self._simple_request()
        elif protocol == SyncProtocol.RR:
            return self._request_response()
        elif protocol == SyncProtocol.RRA:
            return self._request_response_async()
        else:
            raise ValueError(f"Protocolo desconhecido: {protocol}")
    
    def _simple_request(self) -> bool:
        """Protocolo R: Requisição simples sem confirmação"""
        content = self.stub.get_file_content()
        if content is None:
            return False
        
        # Simplesmente salva o conteúdo localmente
        with open('slave.txt', 'w') as f:
            f.write(content)
        return True
    
    def _request_response(self) -> bool:
        """Protocolo RR: Requisição com confirmação síncrona"""
        content = self.stub.get_file_content()
        if content is None:
            return False
        
        # Salva o conteúdo localmente
        with open('slave.txt', 'w') as f:
            f.write(content)
        
        # Envia confirmação de recebimento
        return self.stub.confirm_sync('RR')
    
    def _request_response_async(self) -> bool:
        """Protocolo RRA: Requisição com confirmação assíncrona"""
        content = self.stub.get_file_content()
        if content is None:
            return False
        
        # Salva o conteúdo localmente
        with open('slave.txt', 'w') as f:
            f.write(content)
        
        # Agenda confirmação assíncrona
        self._schedule_async_acknowledgment()
        return True
    
    def _schedule_async_acknowledgment(self):
        """Agenda o acknowledgment assíncrono para ser enviado posteriormente"""
        # Em uma implementação real, isso usaria um sistema de filas ou threads
        # Aqui estamos simplificando com um delay
        import threading
        
        def send_ack():
            time.sleep(2)  # Delay artificial para simular assincronicidade
            self.stub.confirm_sync('RRA')
        
        threading.Thread(target=send_ack).start()
    
    def check_pending_acks(self) -> bool:
        """Verifica se há acknowledgments pendentes"""
        return len(self.pending_acknowledgments) > 0