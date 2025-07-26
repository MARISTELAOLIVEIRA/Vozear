#!/usr/bin/env python3
import os
import sys
sys.path.append('/workspaces/Vozear')

from app import app, descrever_imagem_azure
from dotenv import load_dotenv
import io

load_dotenv()

def testar_azure_cv():
    """Testa a conexão com Azure Computer Vision"""
    try:
        # Criar uma imagem de teste simples (1x1 pixel PNG)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\xe5\'\'|\x00\x00\x00\x00IEND\xaeB`\x82'
        
        print("Testando Azure Computer Vision...")
        resultado = descrever_imagem_azure(png_data)
        print(f"Resultado: {resultado}")
        return True
    except Exception as e:
        print(f"Erro no teste Azure CV: {e}")
        return False

def testar_upload_imagem():
    """Testa upload de imagem via Flask"""
    try:
        with app.test_client() as client:
            # Simular upload de imagem
            data = {
                'texto': '',
                'arquivo': (io.BytesIO(b'fake image data'), 'test.jpg'),
                'url': '',
                'voz': 'pt-BR-FranciscaNeural',
                'velocidade': '+0%'
            }
            
            print("Testando upload de imagem via Flask...")
            response = client.post('/', data=data, content_type='multipart/form-data')
            print(f"Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Erro: {response.data.decode()}")
                return False
            else:
                print("Upload testado com sucesso!")
                return True
                
    except Exception as e:
        print(f"Erro no teste de upload: {e}")
        return False

if __name__ == "__main__":
    print("=== TESTE DE DIAGNÓSTICO ===")
    
    # Teste 1: Azure CV
    print("\n1. Testando Azure Computer Vision...")
    cv_ok = testar_azure_cv()
    
    # Teste 2: Upload Flask
    print("\n2. Testando upload Flask...")
    upload_ok = testar_upload_imagem()
    
    print(f"\n=== RESULTADOS ===")
    print(f"Azure CV: {'✅ OK' if cv_ok else '❌ ERRO'}")
    print(f"Upload: {'✅ OK' if upload_ok else '❌ ERRO'}")
