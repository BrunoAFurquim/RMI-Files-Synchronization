import time
import hashlib
import threading
import os
from pathlib import Path

class SyncMonitor:
    def __init__(self, stub, mode='R', interval=5):
        self.stub = stub
        self.mode = mode
        self.interval = interval
        self.running = False
        self.thread = None
        self.slave_file = Path('client/slave.txt')
        
        # Cria o arquivo slave se não existir
        if not self.slave_file.exists():
            self.slave_file.touch()
    
    def _get_local_hash(self):
        try:
            with open(self.slave_file, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except (FileNotFoundError, PermissionError) as e:
            print(f"[WARN] Não foi possível ler arquivo local: {str(e)}")
            return None
    
    def _sync_file(self):
        try:
            # 1. Verificação de versão com tratamento de erro
            remote_version = self.stub.check_master_version()
            if remote_version is None:
                print("Erro: Não foi possível obter a versão do servidor")
                return
    
            # 2. Obter hash local com tratamento de arquivo ausente
            try:
                local_version = self._get_local_hash()
            except FileNotFoundError:
                local_version = None  # Arquivo slave.txt não existe ainda
    
            # 3. Comparação de versões
            if remote_version != local_version:
                print(f"[SYNC] Alteração detectada (Remota: {remote_version[:8]} != Local: {local_version[:8] if local_version else 'None'})")
                
                # 4. Sincronização do conteúdo
                content = self.stub.get_file_content()
                if content is not None:
                    # 5. Escrita atômica do arquivo
                    temp_path = f"{self.slave_file}.tmp"
                    with open(temp_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    os.replace(temp_path, self.slave_file)
                    
                    print(f"[SYNC] Concluído ({len(content)} bytes transferidos)")
                    
                    # 6. Confirmação para protocolos RR/RRA
                    if self.mode in ['RR', 'RRA']:
                        if not self.stub.confirm_sync(self.mode):
                            print("[SYNC] Aviso: Confirmação não recebida pelo servidor")
    
        except Exception as e:
            print(f"[ERRO] Falha na sincronização: {str(e)}")
            # Log detalhado para debug
            import traceback
            traceback.print_exc()
    
    def _monitor_loop(self):
        while self.running:
            self._sync_file()
            time.sleep(self.interval)
    
    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop)
            self.thread.daemon = True
            self.thread.start()
            print(f"Monitor iniciado. Verificando a cada {self.interval} segundos...")
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()