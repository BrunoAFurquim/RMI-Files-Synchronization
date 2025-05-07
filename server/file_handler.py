from typing import Optional
import os
import hashlib
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_handler.log'),
        logging.StreamHandler()
    ]
)

class FileHandler:
    BASE_DIR = Path(__file__).parent
    MASTER_FILE = BASE_DIR / 'master.txt'
    LOG_FILE = BASE_DIR / 'sync.log'
    USERS_FILE = BASE_DIR / 'users.json'
    
    @classmethod
    def initialize(cls):
        """Inicialização robusta dos arquivos com verificação completa"""
        try:
            cls.BASE_DIR.mkdir(exist_ok=True, mode=0o755)
            
            # Cria master.txt com permissões adequadas
            if not cls.MASTER_FILE.exists():
                with open(cls.MASTER_FILE, 'w', encoding='utf-8') as f:
                    f.write("# Conteúdo inicial\n")
                os.chmod(cls.MASTER_FILE, 0o644)
                logging.info(f"Arquivo master criado em {cls.MASTER_FILE}")
            
            # Inicializa log file como array JSON válido
            if not cls.LOG_FILE.exists():
                with open(cls.LOG_FILE, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                os.chmod(cls.LOG_FILE, 0o644)
            
            # Configura usuários padrão
            if not cls.USERS_FILE.exists():
                default_users = {
                    "admin": "admin123",
                    "user1": "password1"
                }
                with open(cls.USERS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(default_users, f, indent=2)
                os.chmod(cls.USERS_FILE, 0o600)  # Permissões mais restritas
                
            logging.info("Inicialização de arquivos concluída com sucesso")
            
        except PermissionError as pe:
            logging.critical(f"ERRO DE PERMISSÃO: {str(pe)}")
            raise
        except Exception as e:
            logging.critical(f"FALHA NA INICIALIZAÇÃO: {str(e)}")
            raise

    @classmethod
    def get_version(cls) -> str:
        """Obtém a versão atual com tratamento completo de erros"""
        try:
            if not cls.MASTER_FILE.exists():
                cls.initialize()
                
            file_size = os.path.getsize(cls.MASTER_FILE)
            if file_size == 0:
                logging.warning("Arquivo master.txt está vazio")
                return "empty_file"
                
            with open(cls.MASTER_FILE, 'rb') as f:
                content = f.read()
                file_hash = hashlib.md5(content).hexdigest()
                logging.debug(f"Hash calculado: {file_hash}")
                return file_hash
                
        except PermissionError:
            logging.error("Permissão negada para ler master.txt")
            return "permission_denied"
        except Exception as e:
            logging.error(f"ERRO NO GET_VERSION: {str(e)}")
            return "error"

    @classmethod
    def get_content(cls) -> Optional[str]:
        """Obtém o conteúdo do arquivo com tratamento de erros"""
        try:
            if not cls.MASTER_FILE.exists():
                cls.initialize()
                
            with open(cls.MASTER_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                return content if content else None
                
        except Exception as e:
            logging.error(f"ERRO NO GET_CONTENT: {str(e)}")
            return None

    @classmethod
    def log_sync(cls, auth_token: str, mode: str):
        """Registra operações de sincronização de forma segura"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'auth_token': auth_token[:6] + '...',  # Reduz informação sensível
                'mode': mode,
                'status': 'success',
                'client_ip': '127.0.0.1'  # Exemplo, pode ser adaptado
            }
            
            # Cria backup do log atual
            log_backup = cls.LOG_FILE.with_suffix('.bak')
            if cls.LOG_FILE.exists():
                os.replace(cls.LOG_FILE, log_backup)
            
            # Carrega logs existentes ou cria nova lista
            logs = []
            if log_backup.exists():
                try:
                    with open(log_backup, 'r', encoding='utf-8') as f:
                        logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
            
            # Adiciona nova entrada e salva
            logs.append(log_entry)
            with open(cls.LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            logging.error(f"FALHA AO REGISTRAR LOG: {str(e)}")

    @classmethod
    def update_content(cls, new_content: str) -> bool:
        """Atualização segura do arquivo master com rollback"""
        try:
            if not isinstance(new_content, str):
                raise ValueError("Conteúdo deve ser string")
                
            temp_path = f"{cls.MASTER_FILE}.tmp"
            backup_path = f"{cls.MASTER_FILE}.bak"
            
            # Cria backup
            if cls.MASTER_FILE.exists():
                os.replace(cls.MASTER_FILE, backup_path)
            
            # Escreve novo conteúdo em arquivo temporário
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Substitui o arquivo original
            os.replace(temp_path, cls.MASTER_FILE)
            logging.info("Arquivo master atualizado com sucesso")
            return True
            
        except Exception as e:
            logging.error(f"FALHA NA ATUALIZAÇÃO: {str(e)}")
            # Tenta restaurar backup se existir
            if os.path.exists(backup_path):
                os.replace(backup_path, cls.MASTER_FILE)
                logging.warning("Rollback para versão anterior realizado")
            return False