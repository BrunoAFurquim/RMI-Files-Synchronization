RMI File Synchronization System
Overview
Sistema de sincronização de arquivos distribuído utilizando RMI (Remote Method Invocation) em Python, com:

- Sincronização entre arquivo master (servidor) e slave (cliente)
- Três protocolos de comunicação (R, RR, RRA)
- Autenticação segura
- Logs detalhados

🚀 Como Executar o Projeto

- Pré-requisitos
- Python 3.10+
- PowerShell 5.1+ (Windows) ou terminal bash (Linux/Mac)
- Acesso à porta 8000

⚙️ Configuração
Usuários Autorizados
Os usuários são configurados no arquivo server/users.json:

json
{
"admin": "senha_admin",
"usuario1": "senha1",
"usuario2": "senha2"
}
Para adicionar/remover usuários, edite este arquivo e reinicie o servidor.

Protocolos de Sincronismo
Escolha um dos seguintes modos ao iniciar o cliente:

Protocolo Descrição Parâmetro
R Requisição simples --mode R |
RR Requisição-Resposta com confirmação --mode RR |
RRA Requisição-Resposta com confirmação assíncrona --mode RRA

Intervalo de Verificação
Defina o intervalo (em segundos) entre verificações de atualização com --interval (padrão: 5 segundos).

🧪 Testando o Sistema

Inicie o servidor

```
# Configuração definitiva do Python path
$env:PYTHONPATH = "$pwd"

# Execute como módulo Python
python -m server.server_main
```

Execute o cliente em outro terminal:

```
$env:PYTHONPATH = "$pwd"
python -m client.client_main --user admin --password admin123 --mode R --interval 5
```

Edite o arquivo server/master.txt

Verifique a sincronização em client/slave.txt

# Obter token

`$auth = python -c "from common.auth import create_auth_token; print(create_auth_token('admin','senha_admin'))"`

# Testar endpoint
```
$body = @{method="check_master_version"; auth_token=$auth} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:8000/check_master_version" -Method POST -Body $body -Headers @{"Content-Type"="application/json"}
```
📚 Dependências
O projeto utiliza apenas módulos da biblioteca padrão do Python 3.12:

Servidor
http.server: Servidor HTTP básico
threading: Manipulação de threads
json: Serialização de dados
os: Operações com sistema de arquivos
hashlib: Cálculo de hashes para verificação
logging: Registro de logs

Cliente

urllib.request ou http.client: Requisições HTTP
threading: Monitoramento em segundo plano
hashlib: Verificação de versão
argparse: Parsing de argumentos

🏗️ Estrutura do Projeto
sync_rmi_project/
├── client/
│ ├── client_main.py # Ponto de entrada
│ ├── stub.py # Proxy RMI
│ └── sync_monitor.py # Monitor de sincronização
├── server/
│ ├── server_main.py # Servidor principal
│ ├── dispatcher.py # Manipulador de requisições
│ └── file_handler.py # Gerenciamento de arquivos
├── common/
│ ├── auth.py # Autenticação
│ └── protocol.py # Definição de protocolos
├── interface/
│ └── remote_interface.py # Interface RMI
├── README.md
└── requirements.txt # Módulos necessários
🔧 Troubleshooting

Problemas Comuns
Erro de conexão: Verifique se o servidor está rodando e a porta 8000 está livre

Erro de autenticação: Confira users.json e gere novo token

Arquivos não sincronizando: Verifique permissões de arquivo e logs

Logs
server/sync.log: Registro de sincronizações
server/server.log: Logs detalhados do servidor
client/sync_monitor.log: Atividades do cliente
