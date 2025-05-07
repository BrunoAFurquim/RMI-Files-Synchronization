from enum import Enum
import logging
from typing import Callable, Optional
from functools import wraps
import time

class SyncProtocol(Enum):
    R = "Simple Request"
    RR = "Request-Response"
    RRA = "Request-Response with Async Acknowledgment"

def log_protocol_usage(func: Callable):
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
        self.stub = stub
        self.pending_acknowledgments = set()
    
    @log_protocol_usage
    def sync_file(self, protocol: SyncProtocol = SyncProtocol.R) -> bool:
        #Executa a sincronização usando o protocolo especificado
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

        with open('slave.txt', 'w') as f:
            f.write(content)
        return True
    
    def _request_response(self) -> bool:
        """Protocolo RR: Requisição com confirmação síncrona"""
        content = self.stub.get_file_content()
        if content is None:
            return False
        with open('slave.txt', 'w') as f:
            f.write(content)
        return self.stub.confirm_sync('RR')
    
    def _request_response_async(self) -> bool:
        """Protocolo RRA: Requisição com confirmação assíncrona"""
        content = self.stub.get_file_content()
        if content is None:
            return False
        with open('slave.txt', 'w') as f:
            f.write(content)
        self._schedule_async_acknowledgment()
        return True
    
    def _schedule_async_acknowledgment(self):
        import threading
        def send_ack():
            time.sleep(2)
            self.stub.confirm_sync('RRA')
        
        threading.Thread(target=send_ack).start()
    
    def check_pending_acks(self) -> bool:
        return len(self.pending_acknowledgments) > 0