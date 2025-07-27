# 📚 Guia Completo: Flask + Banco de Dados

## 🎯 Como funciona o Flask-SQLAlchemy

### 1. Modelo (Model) = Tabela no banco
```python
class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    comentario = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    aprovado = db.Column(db.Boolean, default=False)
```

Isso cria uma tabela chamada "comentario" com as colunas:
- id (número inteiro, chave primária)
- nome (texto até 100 caracteres, obrigatório)
- comentario (texto longo, obrigatório)
- data_criacao (data/hora, padrão = agora)
- aprovado (verdadeiro/falso, padrão = falso)

### 2. Operações básicas

#### ✅ CRIAR (Create)
```python
# Criar novo comentário
novo_comentario = Comentario(
    nome="João",
    comentario="Ótimo site!"
)
db.session.add(novo_comentario)  # Adiciona à sessão
db.session.commit()              # Salva no banco
```

#### 📖 LER (Read)
```python
# Buscar todos os comentários
todos = Comentario.query.all()

# Buscar comentários aprovados
aprovados = Comentario.query.filter_by(aprovado=True).all()

# Buscar por ID
comentario = Comentario.query.get(1)  # ID = 1

# Buscar primeiro comentário de uma pessoa
primeiro = Comentario.query.filter_by(nome="João").first()
```

#### ✏️ ATUALIZAR (Update)
```python
# Encontrar comentário
comentario = Comentario.query.get(1)

# Modificar
comentario.aprovado = True

# Salvar
db.session.commit()
```

#### ❌ DELETAR (Delete)
```python
# Encontrar comentário
comentario = Comentario.query.get(1)

# Deletar
db.session.delete(comentario)
db.session.commit()
```

### 3. Exemplos práticos do Vozear

#### 💬 Salvar comentário do formulário
```python
@app.route("/sobre", methods=["POST"])
def salvar_comentario():
    nome = request.form.get("nome")
    comentario_texto = request.form.get("comentario")
    
    # Criar novo comentário
    novo_comentario = Comentario(
        nome=nome,
        comentario=comentario_texto
    )
    
    # Salvar no banco
    db.session.add(novo_comentario)
    db.session.commit()
    
    return "Comentário salvo!"
```

#### 📋 Mostrar comentários aprovados
```python
@app.route("/sobre")
def mostrar_pagina():
    # Buscar comentários aprovados
    comentarios = Comentario.query.filter_by(aprovado=True).all()
    
    # Passar para o template
    return render_template("sobre.html", comentarios=comentarios)
```

#### ✅ Aprovar comentário (admin)
```python
@app.route("/admin/aprovar/<int:comentario_id>")
def aprovar_comentario(comentario_id):
    # Encontrar comentário pelo ID
    comentario = Comentario.query.get(comentario_id)
    
    # Aprovar
    comentario.aprovado = True
    
    # Salvar
    db.session.commit()
    
    return "Comentário aprovado!"
```

### 4. Tratamento de erros
```python
try:
    # Operação no banco
    novo_comentario = Comentario(nome="João", comentario="Teste")
    db.session.add(novo_comentario)
    db.session.commit()
    print("✅ Sucesso!")
    
except Exception as e:
    # Se der erro, desfazer mudanças
    db.session.rollback()
    print(f"❌ Erro: {e}")
```

### 5. Inicialização do banco
```python
# Criar todas as tabelas
with app.app_context():
    db.create_all()
```

## 🔄 Fluxo completo no Vozear

1. **Usuário preenche formulário** na página "Sobre"
2. **Flask recebe dados** via POST
3. **Cria objeto Comentario** com os dados
4. **Salva no banco** com db.session.add() + commit()
5. **Admin vê comentários** pendentes na área administrativa
6. **Admin aprova** modificando aprovado=True + commit()
7. **Comentário aparece** na página pública

## 💡 Dicas importantes

### ✅ Sempre fazer commit
```python
# ERRADO - não salva
comentario.aprovado = True

# CERTO - salva no banco
comentario.aprovado = True
db.session.commit()
```

### ✅ Usar try/except para segurança
```python
try:
    db.session.add(novo_item)
    db.session.commit()
except:
    db.session.rollback()  # Desfaz se der erro
```

### ✅ Verificar se existe antes de usar
```python
comentario = Comentario.query.get(comentario_id)
if comentario:
    comentario.aprovado = True
    db.session.commit()
else:
    print("Comentário não encontrado!")
```

## 🏃 Exercícios práticos

1. **Listar todos os comentários**:
   `Comentario.query.all()`

2. **Contar comentários aprovados**:
   `Comentario.query.filter_by(aprovado=True).count()`

3. **Buscar comentários de hoje**:
   `Comentario.query.filter(Comentario.data_criacao >= today).all()`

4. **Deletar comentários antigos**:
   ```python
   antigos = Comentario.query.filter(Comentario.data_criacao < cutoff_date).all()
   for comentario in antigos:
       db.session.delete(comentario)
   db.session.commit()
   ```

O Flask-SQLAlchemy faz todo o trabalho pesado! Você só precisa pensar em objetos Python! 🐍
