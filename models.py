from app import db

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    senha = db.Column(db.String(100))
    tipo = db.Column(db.String(20))  # aluno ou professor
    serie = db.Column(db.String(10), nullable=True)

class Livro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200))
    autor = db.Column(db.String(100))
    link = db.Column(db.String(300))
    capa = db.Column(db.String(300))
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