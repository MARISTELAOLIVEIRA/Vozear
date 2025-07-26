#!/usr/bin/env python3
"""
Script para testar a conectividade com Azure Computer Vision
"""

import os
from dotenv import load_dotenv
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

def test_azure_cv_connection():
    print("=== TESTE DE CONECTIVIDADE AZURE COMPUTER VISION ===")
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    endpoint = os.getenv("AZURE_CV_ENDPOINT")
    key = os.getenv("AZURE_CV_KEY")
    
    print(f"Endpoint carregado: {endpoint}")
    print(f"Key presente: {'Sim' if key else 'Não'}")
    print(f"Key length: {len(key) if key else 0}")
    
    if not endpoint or not key:
        print("❌ ERRO: Credenciais não encontradas!")
        return False
    
    try:
        # Criar cliente
        print("\n📡 Criando cliente Azure CV...")
        client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))
        
        # Testar com uma URL de imagem pública
        test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/User_icon_2.svg/220px-User_icon_2.svg.png"
        
        print(f"🖼️ Testando análise com imagem: {test_image_url}")
        
        # Fazer análise
        analysis = client.analyze_image(
            test_image_url,
            visual_features=[VisualFeatureTypes.description],
            language='pt'
        )
        
        print("\n✅ CONEXÃO ESTABELECIDA COM SUCESSO!")
        
        if analysis.description and analysis.description.captions:
            print(f"📝 Descrição obtida: {analysis.description.captions[0].text}")
            print(f"🎯 Confiança: {analysis.description.captions[0].confidence:.2%}")
        else:
            print("ℹ️ Análise concluída, mas sem descrições disponíveis")
            
        return True
        
    except Exception as e:
        print(f"❌ ERRO na conexão: {e}")
        print(f"🔍 Tipo do erro: {type(e)}")
        
        error_str = str(e).lower()
        if "unauthorized" in error_str or "401" in error_str:
            print("🔑 Problema: Chave de acesso inválida")
        elif "not found" in error_str or "404" in error_str:
            print("🌐 Problema: Endpoint não encontrado")
        elif "forbidden" in error_str or "403" in error_str:
            print("🚫 Problema: Acesso negado - verificar permissões")
        elif "quota" in error_str:
            print("📊 Problema: Cota excedida")
        else:
            print("❓ Problema: Erro desconhecido")
            
        return False

if __name__ == "__main__":
    success = test_azure_cv_connection()
    
    if success:
        print("\n🎉 Teste concluído com SUCESSO!")
        print("✅ As credenciais Azure CV estão funcionando corretamente")
    else:
        print("\n💥 Teste FALHOU!")
        print("❌ Verifique as configurações no portal Azure")
        
    print("\n📋 Próximos passos sugeridos:")
    print("1. Verificar se o serviço Computer Vision está ativo no Azure")
    print("2. Confirmar se as chaves estão corretas no portal")
    print("3. Verificar se há limitações de região")
    print("4. Confirmar se a assinatura está ativa")
