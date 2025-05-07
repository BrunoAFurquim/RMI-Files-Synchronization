from abc import ABC, abstractmethod
from typing import Optional
from common.protocol import SyncProtocol

class RemoteInterface(ABC):
    """
    Interface remota que define todos os métodos disponíveis para invocação remota
    Esta é a definição central do contrato entre cliente e servidor
    """
    
    @abstractmethod
    def get_file_content(self) -> Optional[str]:
        """
        Obtém o conteúdo atual do arquivo master do servidor
        Retorna:
            str: Conteúdo do arquivo se bem-sucedido
            None: Se falhar
        """
        pass
    
    @abstractmethod
    def check_master_version(self) -> Optional[str]:
        """
        Verifica a versão atual do arquivo master
        Retorna:
            str: Hash MD5 ou timestamp da versão atual
            None: Se falhar
        """
        pass
    
    @abstractmethod
    def synchronize(self, protocol: SyncProtocol = SyncProtocol.R) -> bool:
        """
        Inicia o processo de sincronização com o protocolo especificado
        Args:
            protocol: Protocolo de sincronização a ser usado (R, RR ou RRA)
        Retorna:
            bool: True se a sincronização foi iniciada com sucesso
        """
        pass
    
    @abstractmethod
    def confirm_sync(self, protocol_type: str) -> bool:
        """
        Confirma a recepção e gravação do arquivo (usado nos protocolos RR e RRA)
        Args:
            protocol_type: Tipo de protocolo ('RR' ou 'RRA')
        Retorna:
            bool: True se a confirmação foi registrada com sucesso
        """
        pass
    
    @abstractmethod
    def update_master_file(self, new_content: str, auth_token: str) -> bool:
        """
        Atualiza o conteúdo do arquivo master (operação privilegiada)
        Args:
            new_content: Novo conteúdo para o arquivo
            auth_token: Token de autenticação válido
        Retorna:
            bool: True se a atualização foi bem-sucedida
        """
        pass