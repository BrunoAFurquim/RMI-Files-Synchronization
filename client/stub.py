import json
import urllib.request
import time
from urllib.error import URLError, HTTPError
from common.auth import create_auth_token
from interface.remote_interface import RemoteInterface
from common.protocol import SyncProtocol, ProtocolHandler

class FileSyncStub(RemoteInterface):
    def __init__(self, server_url, username, password):
        self.server_url = server_url
        self.auth_token = create_auth_token(username, password)
        self.protocol_handler = ProtocolHandler(self)
        self.retry_delay = 2
        self.max_retries = 3
    
    def _make_request(self, method_name, **kwargs):
        request_data = {
            'method': method_name,
            'auth_token': self.auth_token,
            **kwargs
        }
        
        for attempt in range(self.max_retries):
            try:
                req = urllib.request.Request(
                    url=f"{self.server_url}/{method_name}",
                    data=json.dumps(request_data).encode('utf-8'),
                    headers={'Content-Type': 'application/json', 'Connection': 'keep-alive'},
                    method='POST'
                )
                
                with urllib.request.urlopen(req, timeout=30) as response:
                    if response.status == 200:
                        return json.loads(response.read().decode('utf-8'))
                    else:
                        raise URLError(f"HTTP Error {response.status}")
                    
            except URLError as e:
                print(f"Tentativa {attempt + 1} falhou: {str(e)}")
                if attempt == self.max_retries - 1:
                    return {'status': 'error', 'message': str(e)}
                time.sleep(self.retry_delay)
                
        req = urllib.request.Request(
            url=f"{self.server_url}/{method_name}",
            data=json.dumps(request_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except URLError as e:
            print(f"Erro na comunicação com o servidor: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def confirm_sync(self, protocol_type: str) -> bool:
        """Confirma a sincronização para protocolos RR e RRA"""
        response = self._make_request('confirm_sync', protocol=protocol_type)
        return response.get('status') == 'success'
    
    def get_file_content(self):
        response = self._make_request('get_file_content')
        if response.get('status') == 'success':
            return response.get('content')
        return None
    
    def check_master_version(self):
        response = self._make_request('check_master_version')
        if response.get('status') == 'success':
            return response.get('version')
        return None
    
    def synchronize(self, protocol: SyncProtocol = SyncProtocol.R) -> bool:
        response = self._make_request('synchronize', mode=protocol.value)
        return response.get('status') == 'success'

    def update_master_file(self, new_content: str, auth_token: str) -> bool:
        response = self._make_request(
            'update_master_file',
            new_content=new_content,
            auth_token=auth_token
        )
        return response.get('status') == 'success'