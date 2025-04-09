from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'segredo'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///linkteca.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Importe os modelos aqui, após a inicialização do SQLAlchemy
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    serie = db.Column(db.String(10), nullable=True)
    email = db.Column(db.String(100), nullable=True) # Adicionado campo email

class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    capa = db.Column(db.String(200), nullable=False)
    serie = db.Column(db.String(10), nullable=True)

class Recomendacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'), nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    serie = db.Column(db.String(10), nullable=False)
    livro = db.relationship('Livro', backref='recomendacoes')
    professor = db.relationship('Usuario', backref='recomendacoes')

class AcessoLivro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    data = db.Column(db.DateTime, nullable=False)
    usuario = db.relationship('Usuario', backref='acessos')
    livro = db.relationship('Livro', backref='acessos')


@app.before_request
def criar_banco():
    if not os.path.exists("linkteca.db"):
        with app.app_context():
            db.create_all()

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

@app.route('/painel')
def painel():
    if 'usuario_id' not in session:
        return redirect('/login')
    usuario = Usuario.query.get(session['usuario_id'])
    if usuario.tipo == 'professor':
        return render_template('professor.html', usuario=usuario)
    elif usuario.tipo == 'aluno':
        livros = Livro.query.join(Recomendacao).filter(Recomendacao.serie == usuario.serie).all()
        acessos = AcessoLivro.query.filter_by(usuario_id=usuario.id).order_by(AcessoLivro.data.desc()).limit(5).all()
        return render_template('aluno.html', usuario=usuario, livros=livros, acessos=acessos)
    else:
        return render_template('painel.html', usuario=usuario)

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
        recomendacao = Recomendacao(livro_id=livro.id, professor_id=session['usuario_id'], serie=request.form['serie'])
        db.session.add(recomendacao)
        db.session.commit()
    return redirect('/painel')

@app.route('/baixar/<int:livro_id>')
def baixar_livro(livro_id):
    if 'usuario_id' not in session:
        return redirect('/login')
    acesso = AcessoLivro(usuario_id=session['usuario_id'], livro_id=livro_id, status='baixado', data=datetime.now())
    db.session.add(acesso)
    db.session.commit()
    return redirect(url_for('painel'))

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    session.pop('tipo', None)
    return redirect(url_for('login'))

@app.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form['email']
        # Lógica para enviar email de recuperação de senha (a ser implementada)
        # Aqui você precisaria gerar um token único, salvar no banco de dados
        # associado ao usuário e enviar um email com um link contendo esse token.
        # Por simplicidade, vou apenas imprimir o email.
        print(f"Recuperar senha para o email: {email}")
        return render_template('recuperar_senha_sucesso.html', email=email) # Criar este template
    return render_template('recuperar_senha.html') # Criar este template

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email'] # Obtém o email do formulário
        # Aqui você iria verificar se o email já existe no banco de dados.
        # Se não existir, você cadastra o usuário.  Se existir, informa que
        # o email já está cadastrado.
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            return render_template('cadastro.html', erro_email="Email já cadastrado")
        senha = request.form['senha']
        tipo = request.form['tipo']
        serie = request.form['serie']
        novo_usuario = Usuario(nome=nome, senha=senha, tipo=tipo, serie=serie, email=email) # Inclui o email
        db.session.add(novo_usuario)
        db.session.commit()
        return redirect('/login')  # Redireciona para o login após o cadastro
    return render_template('cadastro.html') #  Criar este template

if __name__ == '__main__':
    app.run(debug=True)