# 📖 Como o banco de dados funciona no SEU Vozear

## 🏗️ Sua estrutura atual

### 1. Modelo Comentario (sua tabela)
```python
class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)           # ID automático
    nome = db.Column(db.String(100), nullable=False)       # Nome obrigatório
    email = db.Column(db.String(100), nullable=True)       # Email opcional  
    comentario = db.Column(db.Text, nullable=False)        # Comentário obrigatório
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)  # Data automática
    aprovado = db.Column(db.Boolean, default=False)        # Inicia como não aprovado
```

Isso cria uma tabela no MySQL assim:
```
+-------------+---------------+------+-----+---------+----------------+
| Campo       | Tipo          | Null | Key | Default | Extra          |
+-------------+---------------+------+-----+---------+----------------+
| id          | int           | NO   | PRI | NULL    | auto_increment |
| nome        | varchar(100)  | NO   |     | NULL    |                |
| email       | varchar(100)  | YES  |     | NULL    |                |
| comentario  | text          | NO   |     | NULL    |                |
| data_criacao| datetime      | YES  |     | now()   |                |
| aprovado    | tinyint(1)    | YES  |     | 0       |                |
+-------------+---------------+------+-----+---------+----------------+
```

## 🔄 Como funciona no seu site

### 1. Usuário deixa comentário (página Sobre)
```python
@app.route("/sobre", methods=["POST"])
def sobre():
    # Pega dados do formulário
    nome = request.form.get("nome")
    email = request.form.get("email") 
    comentario_texto = request.form.get("comentario")
    
    # Cria novo comentário (ainda não aprovado)
    novo_comentario = Comentario(
        nome=nome,
        email=email,
        comentario=comentario_texto
        # aprovado=False (padrão)
        # data_criacao=agora (automático)
    )
    
    # Salva no banco MySQL
    db.session.add(novo_comentario)
    db.session.commit()
    
    # Avisa o usuário
    flash("Comentário enviado! Aguarde moderação.", "success")
```

### 2. Admin vê comentários pendentes
```python
@app.route("/admin/comentarios")
def admin_comentarios():
    # Busca só comentários NÃO aprovados
    pendentes = Comentario.query.filter_by(aprovado=False).all()
    
    # Manda para o template
    return render_template("admin_comentarios.html", comentarios=pendentes)
```

### 3. Admin aprova comentário
```python
@app.route("/admin/aprovar/<int:comentario_id>")
def aprovar_comentario(comentario_id):
    # Encontra o comentário pelo ID
    comentario = Comentario.query.get_or_404(comentario_id)
    
    # Muda para aprovado
    comentario.aprovado = True
    
    # Salva no banco
    db.session.commit()
    
    # Avisa que aprovou
    flash(f"Comentário de {comentario.nome} aprovado!", "success")
```

### 4. Comentários aparecem na página
```python
@app.route("/sobre")
def sobre():
    # Busca só comentários APROVADOS
    comentarios = Comentario.query.filter_by(aprovado=True).all()
    
    # Manda para a página
    return render_template("sobre.html", comentarios=comentarios)
```

## 🛠️ Comandos que você pode usar

### Ver todos os comentários:
```python
todos = Comentario.query.all()
for c in todos:
    print(f"{c.nome}: {c.comentario[:30]}... (Aprovado: {c.aprovado})")
```

### Contar comentários:
```python
total = Comentario.query.count()
aprovados = Comentario.query.filter_by(aprovado=True).count()
pendentes = Comentario.query.filter_by(aprovado=False).count()
```

### Buscar por nome:
```python
comentarios_joao = Comentario.query.filter_by(nome="João").all()
```

### Comentários de hoje:
```python
from datetime import date
hoje = date.today()
comentarios_hoje = Comentario.query.filter(
    db.func.date(Comentario.data_criacao) == hoje
).all()
```

## 🔧 Troubleshooting comum

### ❌ "Table doesn't exist"
```python
# Soluções:
with app.app_context():
    db.create_all()  # Cria todas as tabelas
```

### ❌ "Column doesn't exist" 
```python
# Se você mudou o modelo, precisa recriar:
with app.app_context():
    db.drop_all()    # CUIDADO: Apaga tudo!
    db.create_all()  # Cria novamente
```

### ❌ "Nothing happens"
```python
# Esqueceu o commit:
comentario.aprovado = True
db.session.commit()  # ← ESSENCIAL!
```

### ❌ "Connection error"
```python
# Verificar credenciais MySQL:
print(app.config['SQLALCHEMY_DATABASE_URI'])
```

## 🎯 Seu fluxo atual

1. **MySQL**: `stelaserver.mysql.database.azure.com/vozearbd`
2. **Usuário**: Preenche formulário → Salva como `aprovado=False`
3. **Admin**: Ve pendentes → Aprova → `aprovado=True`
4. **Público**: Vê só aprovados na página

É isso! O Flask faz toda a magia SQL por você! 🪄
