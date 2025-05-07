import argparse
import time
from client.stub import FileSyncStub
from client.sync_monitor import SyncMonitor

def main():
    parser = argparse.ArgumentParser(description="Cliente de sincronização de arquivos RMI")
    parser.add_argument('--server', default='http://localhost:8000', help='Endereço do servidor')
    parser.add_argument('--user', required=True, help='Nome de usuário')
    parser.add_argument('--password', required=True, help='Senha')
    parser.add_argument('--mode', choices=['R', 'RR', 'RRA'], default='R', help='Modo de sincronização')
    parser.add_argument('--interval', type=int, default=5, help='Intervalo de verificação em segundos')
    
    args = parser.parse_args()
    
    # Cria o stub para comunicação com o servidor
    stub = FileSyncStub(args.server, args.user, args.password)
    
    # Inicia o monitor de sincronização
    monitor = SyncMonitor(stub, args.mode, args.interval)
    monitor.start()
    
    try:
        while True:  # Mantém o programa ativo
            time.sleep(1)  
    except KeyboardInterrupt:
        monitor.stop()
        print("Cliente encerrado.")

if __name__ == '__main__':
    main()