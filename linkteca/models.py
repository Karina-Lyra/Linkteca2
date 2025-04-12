from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Tabela de instituições (preenchida pelo professor/admin)
class Instituicao(db.Model):
    __tablename__ = 'instituicao'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

# Tabela de alunos predefinidos pelo professor (valida cadastro do aluno)
class TabelaAluno(db.Model):
    __tablename__ = 'tabela_aluno'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    matricula = db.Column(db.String(20), unique=True, nullable=False)
    instituicao = db.Column(db.String(100), nullable=False)

# Usuários: aluno ou professor
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # aluno ou professor
    serie = db.Column(db.String(10), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    instituicao = db.Column(db.String(100), nullable=True)
    matricula = db.Column(db.String(20), nullable=True)
    primeiro_acesso = db.Column(db.Boolean, default=True)

    acessos = db.relationship('AcessoLivro', backref='usuario', lazy=True)

# Livros cadastrados pelos professores
class Livro(db.Model):
    __tablename__ = 'livro'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    arquivo = db.Column(db.String(200), nullable=False)  # caminho do PDF
    capa = db.Column(db.String(200), nullable=True)
    serie = db.Column(db.String(10), nullable=True)

    acessos = db.relationship('AcessoLivro', backref='livro', lazy=True)

# Acesso, leitura, comentários e avaliações de livros
class AcessoLivro(db.Model):
    __tablename__ = 'acesso_livro'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # baixado, lendo, lido
    data = db.Column(db.DateTime, default=datetime.utcnow)
    comentario = db.Column(db.Text, nullable=True)
    avaliacao = db.Column(db.Integer, nullable=True)  # 1 a 5 estrelas

# Adicione a classe Comentario aqui
class Comentario(db.Model):
    __tablename__ = 'comentario'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    data_comentario = db.Column(db.DateTime, default=datetime.utcnow)
    avaliacao = db.Column(db.Integer, nullable=True)

    usuario = db.relationship('Usuario', backref='comentarios', lazy=True)
    livro = db.relationship('Livro', backref='comentarios', lazy=True)