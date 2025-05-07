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

1. Inicie o Servidor (Terminal 1)

```
# Configuração definitiva do Python path
$env:PYTHONPATH = "$pwd"

# Execute como módulo Python
python -m server.server_main
```

2. Execute o Cliente (Terminal 2)

```
$env:PYTHONPATH = "$pwd"
python -m client.client_main --user admin --password admin123 --mode R --interval 5
```

3. Testando com cURL/PowerShell
   `$auth = python -c "from common.auth import create_auth_token; print(create_auth_token('admin','admin123'))"`

Exemplo: Atualizar Arquivo
powershell

```
    $body = @{
        method = "update_master_file"
        auth_token = $auth
        new_content = "Novo conteúdo com acentuação çãõ"
    } | ConvertTo-Json -Compress
    Invoke-WebRequest -Uri "http://localhost:8000/update_master_file" -Method POST -Body $body -Headers @{"Content-Type"="application/json"}
```
