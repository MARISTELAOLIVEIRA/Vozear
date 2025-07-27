# 🔍 Verificar Variáveis de Ambiente no Azure

## No Azure App Service, verificar se alguma dessas variáveis existe automaticamente:

### 1. CONNECTION STRINGS (mais comum):
- `MYSQLCONNSTR_defaultConnection`
- `SQLCONNSTR_DefaultConnection` 
- `DATABASE_URL`

### 2. Se não existir, criar manualmente:
```
DB_HOST=stelaserver.mysql.database.azure.com
DB_USER=maristela
DB_PASSWORD=AdmSt3l@2025
DB_NAME=vozearbd
DB_PORT=3306
```

### 3. Ou usar CONNECTION STRING (mais parecido com Django):
```
DATABASE_URL=mysql://maristela:AdmSt3l@2025@stelaserver.mysql.database.azure.com:3306/vozearbd
```

## Como verificar no Azure:
1. App Service → Configuration
2. Ver se já existe alguma connection string
3. Se não, adicionar as variáveis

O código agora tenta todas as opções automaticamente!
