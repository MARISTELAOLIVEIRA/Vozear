from flask import Flask, render_template, request, send_from_directory
import os
from datetime import datetime, timedelta
import asyncio
import edge_tts
import fitz
import time
import threading

app = Flask(__name__)
AUDIO_FOLDER = "audio"
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or '78754f9651a49e373a8a59277976e9c00c59914b53f5abef33cfa67669a3661d'

os.makedirs(AUDIO_FOLDER, exist_ok=True)

TEMPO_RETENCAO_SEGUNDOS_TESTE = 60 * 5  # Manter arquivos por 5 minuto para teste

def limpar_arquivos_temporarios():
    while True:
        agora = datetime.now()
        arquivos_excluidos = 0
        for nome_arquivo in os.listdir(AUDIO_FOLDER):
            caminho_arquivo = os.path.join(AUDIO_FOLDER, nome_arquivo)
            try:
                data_modificacao = datetime.fromtimestamp(os.path.getmtime(caminho_arquivo))
                if agora - data_modificacao > timedelta(seconds=TEMPO_RETENCAO_SEGUNDOS_TESTE):
                    os.remove(caminho_arquivo)
                    print(f"Arquivo temporário excluído: {caminho_arquivo}")
                    arquivos_excluidos += 1
            except Exception as e:
                print(f"Erro ao verificar/excluir arquivo {nome_arquivo}: {e}")
        if arquivos_excluidos > 0:
            print(f"Rotina de limpeza: {arquivos_excluidos} arquivos excluídos.")
        time.sleep(120)  # Executar a cada 120 segundos

thread_limpeza = threading.Thread(target=limpar_arquivos_temporarios, daemon=True)
thread_limpeza.start()


def extrair_texto_pdf(caminho_pdf):
    documento = fitz.open(caminho_pdf)
    texto = ""
    for pagina in documento:
        texto += pagina.get_text()
    return texto

# Função para exibir a página sobre o aplicativo
@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


@app.route("/", methods=["GET", "POST"])
def index():
    audio_file = None

    if request.method == "POST":
        texto = request.form.get("texto")
        arquivo = request.files.get("arquivo")
        if texto and texto.strip():
            texto_final = texto
        elif arquivo:
            caminho_pdf = os.path.join(AUDIO_FOLDER, arquivo.filename)
            arquivo.save(caminho_pdf)
            texto_final = extrair_texto_pdf(caminho_pdf)
        else:
            texto_final = None

        if texto_final:
            nome_arquivo = f"audio_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
            caminho = os.path.join(AUDIO_FOLDER, nome_arquivo)

            voice = request.form.get("voz", "pt-BR-AntonioNeural")
            rate = request.form.get("velocidade", "+0%")

            async def gerar_audio():
                try:
                    communicate = edge_tts.Communicate(texto_final, voice, rate=rate)
                    await communicate.save(caminho)
                    print(f"Áudio gerado: {caminho}")
                except Exception as e:
                    print(f"Erro ao gerar áudio: {e}")

            asyncio.run(gerar_audio())
            audio_file = nome_arquivo

    return render_template("index.html", audio_file=audio_file)

@app.route("/audio/<filename>")
def audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

if __name__ == "__main__":
    app.run()