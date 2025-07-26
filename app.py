from flask import Flask, render_template, request, send_from_directory
import os
from datetime import datetime, timedelta
import asyncio
import edge_tts
import fitz
import time
import threading
import io
from dotenv import load_dotenv
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

load_dotenv()

app = Flask(__name__)
AUDIO_FOLDER = "audio"
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or '78754f9651a49e373a8a59277976e9c00c59914b53f5abef33cfa67669a3661d'

os.makedirs(AUDIO_FOLDER, exist_ok=True)

TEMPO_RETENCAO_SEGUNDOS_TESTE = 60 * 5


def limpar_arquivos_temporarios():
    while True:
        agora = datetime.now()
        for nome_arquivo in os.listdir(AUDIO_FOLDER):
            caminho_arquivo = os.path.join(AUDIO_FOLDER, nome_arquivo)
            try:
                data_modificacao = datetime.fromtimestamp(os.path.getmtime(caminho_arquivo))
                if agora - data_modificacao > timedelta(seconds=TEMPO_RETENCAO_SEGUNDOS_TESTE):
                    os.remove(caminho_arquivo)
            except Exception as e:
                print(f"Erro ao verificar/excluir arquivo {nome_arquivo}: {e}")
        time.sleep(120)

thread_limpeza = threading.Thread(target=limpar_arquivos_temporarios, daemon=True)
thread_limpeza.start()

def extrair_texto_pdf(caminho_pdf):
    documento = fitz.open(caminho_pdf)
    texto = ""
    for pagina in documento:
        texto += pagina.get_text()
    return texto

def extrair_imagens_pdf(caminho_pdf):
    documento = fitz.open(caminho_pdf)
    imagens = []
    for page in documento:
        imagens_da_pagina = page.get_images(full=True)
        for img in imagens_da_pagina:
            xref = img[0]
            base_image = documento.extract_image(xref)
            imagens.append(base_image["image"])
    return imagens

def descrever_imagem_azure(image_bytes):
    endpoint = os.getenv("AZURE_CV_ENDPOINT")
    key = os.getenv("AZURE_CV_KEY")
    
    if not endpoint or not key:
        return "Configuração do Azure Computer Vision não encontrada."

    try:
        # Garantir que o endpoint tenha a barra final
        if not endpoint.endswith('/'):
            endpoint += '/'
            
        client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))
        
        # Usar a análise mais robusta
        analysis = client.analyze_image_in_stream(
            io.BytesIO(image_bytes), 
            visual_features=['Description'],
            language='pt'
        )
        
        if analysis.description and analysis.description.captions:
            return analysis.description.captions[0].text
        else:
            return "Imagem processada com sucesso. Descrição automática não disponível para esta imagem."
            
    except Exception as e:
        error_msg = str(e).lower()
        if "not found" in error_msg or "404" in error_msg:
            return "Imagem carregada com sucesso. O serviço Azure Computer Vision está temporariamente indisponível."
        elif "unauthorized" in error_msg or "forbidden" in error_msg or "401" in error_msg or "403" in error_msg:
            return "Imagem carregada com sucesso. Credenciais do Azure Computer Vision precisam ser renovadas."
        else:
            print(f"Erro Azure CV: {e}")
            return "Imagem carregada com sucesso. Processamento automático de descrição temporariamente indisponível."

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/", methods=["GET", "POST"])
def index():
    audio_file = None
    if request.method == "POST":
        try:
            texto = request.form.get("texto")
            arquivo = request.files.get("arquivo")
            texto_final = ""
            url = request.form.get("url")
            
            if url:
                try:
                    import requests
                    from bs4 import BeautifulSoup

                    response = requests.get(url, timeout=10)
                    soup = BeautifulSoup(response.content, "html.parser")

                    # Tenta extrair o conteúdo principal
                    artigos = soup.find_all(["article", "p", "h1", "h2"])
                    texto_extraido = "\n".join([tag.get_text() for tag in artigos if tag.get_text().strip()])
                    texto_final = texto_extraido if texto_extraido else "Não foi possível extrair conteúdo legível do site."
                except Exception as e:
                    print(f"Erro ao processar URL: {e}")
                    texto_final = f"Ocorreu um erro ao acessar a URL: {str(e)}"

            if texto and texto.strip():
                texto_final = texto
            elif arquivo:
                extensao = os.path.splitext(arquivo.filename)[1].lower()
                caminho_arquivo = os.path.join(AUDIO_FOLDER, arquivo.filename)
                arquivo.save(caminho_arquivo)

                if extensao == '.pdf':
                    try:
                        texto_extraido = extrair_texto_pdf(caminho_arquivo)
                        texto_final += texto_extraido
                        imagens = extrair_imagens_pdf(caminho_arquivo)
                        for idx, img_bytes in enumerate(imagens, start=1):
                            try:
                                descricao = descrever_imagem_azure(img_bytes)
                                texto_final += f"\nDescrição da imagem {idx}: {descricao}\n"
                            except Exception as e:
                                print(f"Erro ao processar imagem {idx} do PDF: {e}")
                                texto_final += f"\nImagem {idx} encontrada no PDF (descrição indisponível)\n"
                    except Exception as e:
                        print(f"Erro ao processar PDF: {e}")
                        texto_final = f"Erro ao processar arquivo PDF: {str(e)}"
                elif extensao in ALLOWED_IMAGE_EXTENSIONS:
                    try:
                        with open(caminho_arquivo, "rb") as img_file:
                            image_bytes = img_file.read()
                            descricao = descrever_imagem_azure(image_bytes)
                            texto_final = f"Descrição da imagem: {descricao}"
                    except Exception as e:
                        print(f"Erro ao processar imagem: {e}")
                        texto_final = f"Imagem carregada, mas ocorreu um erro ao processá-la: {str(e)}"
                else:
                    texto_final = "Formato de arquivo não suportado."

            if texto_final:
                nome_arquivo = f"audio_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
                caminho = os.path.join(AUDIO_FOLDER, nome_arquivo)
                voice = request.form.get("voz", "pt-BR-AntonioNeural")
                rate = request.form.get("velocidade", "+0%")
                
                async def gerar_audio():
                    try:
                        communicate = edge_tts.Communicate(texto_final, voice, rate=rate)
                        await communicate.save(caminho)
                        print(f"Áudio gerado com sucesso: {caminho}")
                    except Exception as e:
                        print(f"Erro ao gerar áudio: {e}")
                        raise e
                        
                asyncio.run(gerar_audio())
                audio_file = nome_arquivo
                
        except Exception as e:
            print(f"Erro geral na aplicação: {e}")
            import traceback
            traceback.print_exc()
            return f"Erro interno: {str(e)}", 500

    return render_template("index.html", audio_file=audio_file)

@app.route("/audio/<filename>")
def audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

@app.route("/som/sucesso")
def som_sucesso():
    return send_from_directory('static', 'sucesso.mp3')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
