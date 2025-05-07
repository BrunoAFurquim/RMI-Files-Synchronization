import sys
from pathlib import Path

# Adiciona o diretório raiz ao Python path
sys.path.append(str(Path(__file__).parent))

from client.client_main import main

if __name__ == '__main__':
    main()