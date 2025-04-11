from app import db

# Tabela da Instituição
class Instituicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=True)

# Tabela para o usuário administrador do sistema
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    trocar_senha = db.Column(db.Boolean, default=True)  # Trocar no 1º acesso

# Usuários comuns: aluno ou professor
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20))  # aluno ou professor
    serie = db.Column(db.String(10), nullable=True)
    primeiro_acesso = db.Column(db.Boolean, default=True)

class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(300), nullable=False)
    capa = db.Column(db.String(300), nullable=False)
    serie = db.Column(db.String(10))

class Recomendacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'))
    professor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    serie = db.Column(db.String(10))

class AcessoLivro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    livro_id = db.Column(db.Integer, db.ForeignKey('livro.id'))
    status = db.Column(db.String(20))
    data = db.Column(db.DateTime)
    comentario = db.Column(db.Text, nullable=True)
    avaliacao = db.Column(db.Integer, nullable=True)
