#!/usr/bin/env python3
"""
Script para testar conectividade MySQL no Azure
"""

import os
from dotenv import load_dotenv
import pymysql

def test_mysql_connection():
    print("=== TESTE DE CONECTIVIDADE MYSQL AZURE ===")
    
    load_dotenv()
    
    # Tentar connection string automática primeiro (MySQL in App)
    mysql_conn_str = os.environ.get('MYSQLCONNSTR_defaultConnection')
    if mysql_conn_str:
        print("🔍 MySQL in App detectado!")
        print(f"Connection String: {mysql_conn_str[:50]}...")
        # Parse connection string seria necessário aqui
        return test_mysql_in_app(mysql_conn_str)
    
    # Tentar variáveis manuais
    host = os.environ.get('MYSQL_HOST')
    user = os.environ.get('MYSQL_USER')
    password = os.environ.get('MYSQL_PASSWORD')
    database = os.environ.get('MYSQL_DATABASE')
    
    print(f"Host: {host}")
    print(f"User: {user}")
    print(f"Database: {database}")
    print(f"Password presente: {'Sim' if password else 'Não'}")
    
    if not all([host, user, password, database]):
        print("❌ ERRO: Credenciais MySQL não encontradas!")
        print("\n💡 Configure as variáveis:")
        print("MYSQL_HOST=<host>")
        print("MYSQL_USER=<usuario>")
        print("MYSQL_PASSWORD=<senha>")
        print("MYSQL_DATABASE=<banco>")
        return False
    
    return test_mysql_manual(host, user, password, database)

def test_mysql_manual(host, user, password, database):
    try:
        print(f"\n📡 Conectando em {host}...")
        
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            connect_timeout=10
        )
        
        print("✅ CONEXÃO MYSQL ESTABELECIDA!")
        
        # Testar operações básicas
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"📊 Versão MySQL: {version[0]}")
            
            cursor.execute("SELECT DATABASE()")
            current_db = cursor.fetchone()
            print(f"🗄️ Banco atual: {current_db[0]}")
            
            # Testar criação de tabela
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_vozear (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(100),
                    teste DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Teste de criação de tabela: OK")
            
            # Testar inserção
            cursor.execute("INSERT INTO test_vozear (nome) VALUES (%s)", ("Teste Vozear",))
            connection.commit()
            print("✅ Teste de inserção: OK")
            
            # Testar seleção
            cursor.execute("SELECT COUNT(*) FROM test_vozear")
            count = cursor.fetchone()
            print(f"✅ Teste de consulta: {count[0]} registros")
            
            # Limpar teste
            cursor.execute("DROP TABLE test_vozear")
            connection.commit()
            print("✅ Limpeza: OK")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ ERRO na conexão MySQL: {e}")
        print(f"🔍 Tipo do erro: {type(e)}")
        
        error_str = str(e).lower()
        if "access denied" in error_str:
            print("🔑 Problema: Usuário/senha incorretos")
        elif "unknown host" in error_str:
            print("🌐 Problema: Host não encontrado")
        elif "timeout" in error_str:
            print("⏰ Problema: Timeout de conexão")
        elif "unknown database" in error_str:
            print("🗄️ Problema: Banco de dados não existe")
        else:
            print("❓ Problema: Erro desconhecido")
            
        return False

def test_mysql_in_app(conn_str):
    print("🔧 Função para MySQL in App ainda não implementada")
    print("Use variáveis manuais por enquanto")
    return False

if __name__ == "__main__":
    success = test_mysql_connection()
    
    if success:
        print("\n🎉 Teste MySQL concluído com SUCESSO!")
        print("✅ O banco MySQL está funcionando corretamente")
        print("\n🚀 Próximo passo: fazer deploy da aplicação")
    else:
        print("\n💥 Teste MySQL FALHOU!")
        print("❌ Verifique as configurações do MySQL")
        print("\n📖 Consulte MYSQL_SETUP.md para instruções")
