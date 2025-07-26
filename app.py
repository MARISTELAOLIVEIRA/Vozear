from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from functools import wraps
import os
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

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vozear_comentarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Modelo de Comentário
class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    comentario = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    aprovado = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Comentario {self.nome}: {self.comentario[:50]}...>'

# Criar tabelas
with app.app_context():
    db.create_all()

# Configurações de admin
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "vozear2025"  # Mude para uma senha mais segura em produção

# Decorador para proteger rotas admin
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

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

@app.route("/sobre", methods=["GET", "POST"])
def sobre():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email", "")
        comentario_texto = request.form.get("comentario")
        
        if nome and comentario_texto:
            novo_comentario = Comentario(
                nome=nome,
                email=email,
                comentario=comentario_texto
            )
            db.session.add(novo_comentario)
            db.session.commit()
            flash("Comentário enviado com sucesso! Aguardando moderação.", "success")
            return redirect(url_for('sobre'))
        else:
            flash("Por favor, preencha pelo menos o nome e o comentário.", "error")
    
    # Buscar comentários aprovados
    comentarios_aprovados = Comentario.query.filter_by(aprovado=True).order_by(Comentario.data_criacao.desc()).all()
    
    return render_template("sobre.html", comentarios=comentarios_aprovados)

# Rota de login admin
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['admin_user'] = username
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('admin_comentarios'))
        else:
            flash("Usuário ou senha incorretos!", "error")
    
    return render_template("admin_login.html")

# Rota de logout admin
@app.route("/admin/logout")
def admin_logout():
    session.pop('logged_in', None)
    session.pop('admin_user', None)
    flash("Logout realizado com sucesso!", "success")
    return redirect(url_for('admin_login'))

# Rota para moderar comentários (agora protegida)
@app.route("/admin/comentarios")
@login_required
def admin_comentarios():
    comentarios_pendentes = Comentario.query.filter_by(aprovado=False).order_by(Comentario.data_criacao.desc()).all()
    return render_template("admin_comentarios.html", comentarios=comentarios_pendentes)

# Rota para visualizar todo o banco de dados (agora protegida)
@app.route("/admin/banco")
@login_required
def admin_banco():
    todos_comentarios = Comentario.query.order_by(Comentario.data_criacao.desc()).all()
    total_comentarios = len(todos_comentarios)
    aprovados = len([c for c in todos_comentarios if c.aprovado])
    pendentes = len([c for c in todos_comentarios if not c.aprovado])
    
    return render_template("admin_banco.html", 
                         comentarios=todos_comentarios,
                         total=total_comentarios,
                         aprovados=aprovados,
                         pendentes=pendentes)

@app.route("/admin/aprovar/<int:comentario_id>")
@login_required
def aprovar_comentario(comentario_id):
    comentario = Comentario.query.get_or_404(comentario_id)
    comentario.aprovado = True
    db.session.commit()
    flash(f"Comentário de {comentario.nome} aprovado!", "success")
    return redirect(url_for('admin_comentarios'))

@app.route("/admin/rejeitar/<int:comentario_id>")
@login_required
def rejeitar_comentario(comentario_id):
    comentario = Comentario.query.get_or_404(comentario_id)
    db.session.delete(comentario)
    db.session.commit()
    flash(f"Comentário de {comentario.nome} rejeitado!", "warning")
    return redirect(url_for('admin_comentarios'))

@app.route("/admin/excluir/<int:comentario_id>")
@login_required
def excluir_comentario(comentario_id):
    comentario = Comentario.query.get_or_404(comentario_id)
    nome_usuario = comentario.nome
    db.session.delete(comentario)
    db.session.commit()
    flash(f"Comentário de {nome_usuario} excluído permanentemente!", "error")
    return redirect(request.referrer or url_for('admin_banco'))

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
    app.run(debug=True, host="0.0.0.0", port=5002)
