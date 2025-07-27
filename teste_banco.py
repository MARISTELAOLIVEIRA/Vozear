#!/usr/bin/env python3
"""
Script para testar a criação do banco de dados e inserir um comentário de teste
"""

import sys
sys.path.append('.')

from app import app, db, Comentario
from datetime import datetime

def teste_banco():
    with app.app_context():
        print("🔍 Testando criação do banco de dados...")
        
        # Criar tabelas
        db.create_all()
        print("✅ Tabelas criadas com sucesso!")
        
        # Inserir comentário de teste
        comentario_teste = Comentario(
            nome="Teste Sistema",
            email="teste@vozear.com",
            comentario="Este é um comentário de teste para verificar se o banco está funcionando!"
        )
        
        db.session.add(comentario_teste)
        db.session.commit()
        print("✅ Comentário de teste inserido!")
        
        # Verificar se foi salvo
        comentarios = Comentario.query.all()
        print(f"📊 Total de comentários no banco: {len(comentarios)}")
        
        for c in comentarios:
            print(f"   - {c.nome}: {c.comentario[:50]}...")
            
        print("🎉 Teste concluído com sucesso!")

if __name__ == "__main__":
    teste_banco()
