from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'segredo'

# Configurações do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///linkteca.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o SQLAlchemy
db = SQLAlchemy(app)

# MODELOS
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # aluno ou professor
    serie = db.Column(db.String(10), nullable=True)
    email = db.Column(db.String(100), nullable=True)

    acessos = db.relationship('AcessoLivro', backref='usuario', lazy=True)
    recomendacoes = db.relationship('Recomendacao', backref='professor', lazy=True)

class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    capa = db.Column(db.String(200), nullable=False)
    serie = db.Column(db.String(10), nullable=True)

    acessos = db.relationship('AcessoLivro', backref='livro', lazy=True)
    recomendacoes = db.relationship('Recomendacao', backref='livro', lazy=True)

class Recomendacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    serie = db.Column(db.String(10), nullable=False)

class AcessoLivro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # baixado, lendo, lido
    data = db.Column(db.DateTime, nullable=False)
    comentario = db.Column(db.Text, nullable=True)
    avaliacao = db.Column(db.Integer, nullable=True)  # 1 a 5 estrelas

class Instituicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=True)

# CRIAR BANCO AUTOMATICAMENTE SE NÃO EXISTIR


# ROTAS PRINCIPAIS
@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(nome=nome, senha=senha).first()
        if usuario:
            session['usuario_id'] = usuario.id
            session['tipo'] = usuario.tipo
            return redirect('/painel')
        else:
            return render_template('login.html', erro="Usuário ou senha incorretos")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    session.pop('tipo', None)
    return redirect('/login')

@app.route('/painel')
def painel():
    if 'usuario_id' not in session:
        return redirect('/login')
    usuario = Usuario.query.get(session['usuario_id'])

    if usuario.tipo == 'admin':
        instituicao = Instituicao.query.first()
        return render_template('admin.html', admin=usuario, instituicao=instituicao)

    elif usuario.tipo == 'professor':
        return render_template('professor.html', usuario=usuario)

    elif usuario.tipo == 'aluno':
        livros = Livro.query.join(Recomendacao).filter(Recomendacao.serie == usuario.serie).all()
        acessos = AcessoLivro.query.filter_by(usuario_id=usuario.id).order_by(AcessoLivro.data.desc()).limit(5).all()
        return render_template('aluno.html', usuario=usuario, livros=livros, acessos=acessos)

    return redirect('/login')


@app.route('/recomendar', methods=['POST'])
def recomendar():
    if 'usuario_id' in session and session['tipo'] == 'professor':
        livro = Livro(
            titulo=request.form['titulo'],
            autor=request.form['autor'],
            link=request.form['link'],
            capa=request.form['capa'],
            serie=request.form['serie']
        )
        db.session.add(livro)
        db.session.commit()
        recomendacao = Recomendacao(
            livro_id=livro.id,
            professor_id=session['usuario_id'],
            serie=request.form['serie']
        )
        db.session.add(recomendacao)
        db.session.commit()
    return redirect('/painel')

@app.route('/baixar/<int:livro_id>')
def baixar_livro(livro_id):
    if 'usuario_id' not in session:
        return redirect('/login')
    acesso = AcessoLivro(
        usuario_id=session['usuario_id'],
        livro_id=livro_id,
        status='baixado',
        data=datetime.now()
    )
    db.session.add(acesso)
    db.session.commit()
    return redirect(url_for('painel'))

@app.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form['email']
        print(f"Recuperar senha para o email: {email}")
        return render_template('recuperar_senha_sucesso.html', email=email)
    return render_template('recuperar_senha.html')

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        tipo = request.form['tipo']
        serie = request.form['serie']

        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            return render_template('cadastro.html', erro_email="Email já cadastrado")

        novo_usuario = Usuario(nome=nome, senha=senha, tipo=tipo, serie=serie, email=email)
        db.session.add(novo_usuario)
        db.session.commit()
        return redirect('/login')
    return render_template('cadastro.html')

def criar_admin_padrao():
    admin_existente = Usuario.query.filter_by(nome='Administrador', tipo='admin').first()
    if not admin_existente:
        admin = Usuario(nome='Administrador', senha='admin123', tipo='admin')
        db.session.add(admin)
        db.session.commit()
        print("✅ Usuário Administrador criado.")
    else:
        print("🔒 Administrador já existe.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Isso é seguro, não recria dados se já existir
        criar_admin_padrao()
    app.run(debug=True)