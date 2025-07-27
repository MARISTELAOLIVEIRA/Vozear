#!/usr/bin/env python3
"""
Teste de conexão com o banco MySQL vozeardb
"""

import os
from dotenv import load_dotenv

def test_vozeardb_connection():
    print("=== TESTE DE CONEXÃO VOZEARDB ===")
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    mysql_host = os.getenv('DB_HOST') or os.getenv('MYSQL_HOST')
    mysql_user = os.getenv('DB_USER') or os.getenv('MYSQL_USER')
    mysql_password = os.getenv('DB_PASSWORD') or os.getenv('MYSQL_PASSWORD')
    mysql_database = os.getenv('DB_NAME') or os.getenv('MYSQL_DATABASE', 'vozearbd')
    mysql_port = int(os.getenv('DB_PORT', '3306'))
    
    print(f"🏠 Host: {mysql_host}:{mysql_port}")
    print(f"👤 User: {mysql_user}")
    print(f"🗄️ Database: {mysql_database}")
    print(f"🔑 Password: {'Configurada' if mysql_password else 'Não encontrada'}")
    
    if not mysql_host or not mysql_user or not mysql_password:
        print("\n❌ ERRO: Credenciais MySQL não configuradas!")
        print("\n📋 Configure as variáveis no .env:")
        print("DB_HOST=seu-servidor.mysql.database.azure.com")
        print("DB_USER=seu-usuario")
        print("DB_PASSWORD=sua-senha-forte")
        print("DB_NAME=vozearbd")
        print("DB_PORT=3306")
        return False
    
    try:
        print(f"\n📡 Testando conexão com {mysql_host}...")
        
        import pymysql
        connection = pymysql.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database,
            charset='utf8mb4',
            ssl={'ssl_disabled': False}
        )
        
        print("✅ CONEXÃO ESTABELECIDA COM SUCESSO!")
        
        # Testar criação de tabela de teste
        cursor = connection.cursor()
        
        # Teste básico
        cursor.execute("SELECT VERSION();")
        version = cursor.fetchone()
        print(f"🐬 Versão MySQL: {version[0]}")
        
        # Listar tabelas
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print(f"📊 Tabelas existentes: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        connection.close()
        
        print("\n🎉 Banco vozeardb pronto para uso!")
        return True
        
    except ImportError:
        print("❌ ERRO: PyMySQL não instalado!")
        print("Execute: pip install PyMySQL")
        return False
        
    except Exception as e:
        print(f"❌ ERRO na conexão: {e}")
        
        error_str = str(e).lower()
        if "access denied" in error_str:
            print("🔑 Problema: Usuário/senha incorretos")
        elif "unknown database" in error_str:
            print("🗄️ Problema: Banco 'vozeardb' não existe")
        elif "can't connect" in error_str:
            print("🌐 Problema: Não consegue conectar ao servidor")
        elif "timeout" in error_str:
            print("⏰ Problema: Timeout na conexão")
        else:
            print("❓ Problema: Erro desconhecido")
            
        return False

def test_sqlalchemy_connection():
    """Testa conexão usando SQLAlchemy (igual ao app)"""
    print("\n=== TESTE SQLALCHEMY ===")
    
    try:
        from app import get_database_uri
        uri = get_database_uri()
        
        print(f"📝 URI: {uri.split('@')[0]}@...")
        
        from sqlalchemy import create_engine, text
        engine = create_engine(uri)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            print(f"✅ SQLAlchemy OK: {test_value}")
            
        return True
        
    except Exception as e:
        print(f"❌ SQLAlchemy erro: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testando conexão com vozeardb...")
    
    success1 = test_vozeardb_connection()
    success2 = test_sqlalchemy_connection()
    
    if success1 and success2:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ O Vozear está pronto para usar MySQL!")
    else:
        print("\n💥 ALGUNS TESTES FALHARAM!")
        print("❌ Verifique as configurações do MySQL")
