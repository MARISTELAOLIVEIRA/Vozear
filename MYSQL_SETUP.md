# 🗄️ Configuração MySQL no Azure para Vozear

## Opção 1: Azure Database for MySQL (Recomendado)

### Passo 1: Criar o serviço MySQL
```bash
# Via Azure CLI
az mysql flexible-server create \
  --resource-group <seu-resource-group> \
  --name vozear-mysql \
  --admin-user vozearadmin \
  --admin-password <senha-forte> \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --public-access 0.0.0.0 \
  --storage-size 20 \
  --location eastus
```

### Passo 2: Criar banco de dados vozeardb
```sql
CREATE DATABASE vozeardb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Passo 3: Configurar variáveis de ambiente no Azure App Service
No portal Azure → App Service → Configuration → Application settings:

```
DB_HOST=seu-servidor.mysql.database.azure.com
DB_USER=seu-usuario
DB_PASSWORD=sua-senha-forte
DB_NAME=seu-banco
DB_PORT=3306
```

---

## Opção 2: MySQL in App (Mais simples)

### Passo 1: Ativar MySQL in App
1. Portal Azure → App Service → MySQL in App
2. Ativar MySQL in App
3. O Azure criará automaticamente as credenciais

### Passo 2: Usar variáveis automáticas
O Azure define automaticamente:
- `MYSQLCONNSTR_defaultConnection`

### Passo 3: Atualizar código (se usar MySQL in App)
```python
# No app.py, adicionar suporte para connection string automática:
def get_database_uri():
    # MySQL in App (Azure automático)
    mysql_conn_str = os.environ.get('MYSQLCONNSTR_defaultConnection')
    if mysql_conn_str:
        # Converter connection string para SQLAlchemy format
        # Formato: Database=<db>;Data Source=<host>;User Id=<user>;Password=<pass>
        import re
        match = re.search(r'Database=([^;]+).*Data Source=([^;]+).*User Id=([^;]+).*Password=([^;]+)', mysql_conn_str)
        if match:
            db, host, user, password = match.groups()
            return f"mysql+pymysql://{user}:{password}@{host}/{db}?charset=utf8mb4"
    
    # Tentar MySQL manual
    mysql_host = os.environ.get('MYSQL_HOST')
    mysql_user = os.environ.get('MYSQL_USER') 
    mysql_password = os.environ.get('MYSQL_PASSWORD')
    mysql_database = os.environ.get('MYSQL_DATABASE')
    
    if mysql_host and mysql_user and mysql_password and mysql_database:
        return f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}?charset=utf8mb4"
    else:
        # Fallback SQLite
        return 'sqlite:///vozear_comentarios.db'
```

---

## Passo 4: Testar Conexão

Criar arquivo `test_mysql.py`:
```python
import os
from dotenv import load_dotenv
import pymysql

load_dotenv()

def test_mysql():
    host = os.getenv('MYSQL_HOST')
    user = os.getenv('MYSQL_USER')
    password = os.getenv('MYSQL_PASSWORD')
    database = os.getenv('MYSQL_DATABASE')
    
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        print("✅ Conexão MySQL funcionando!")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ Erro MySQL: {e}")
        return False

if __name__ == "__main__":
    test_mysql()
```

---

## Vantagens MySQL vs SQLite:

### ✅ MySQL:
- Mais estável em produção
- Suporte a múltiplas conexões
- Backup automático (Azure)
- Melhor performance para múltiplos usuários
- Tipos de dados mais ricos

### ❌ SQLite:
- Arquivo local (pode ser perdido)
- Problemas com múltiplas conexões
- Sem backup automático
- Limitações de concorrência

---

## 💰 Custos estimados:
- **MySQL in App**: Gratuito (limitado)
- **Azure Database for MySQL**: ~$15-30/mês (tier básico)

## 🚀 Recomendação:
1. Comece com **MySQL in App** para testes
2. Migre para **Azure Database for MySQL** para produção séria
