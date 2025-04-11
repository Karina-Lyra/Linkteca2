from flask import Blueprint, render_template, request, redirect, session, url_for
from datetime import datetime
from linkteca.models import db, Usuario, Livro, Recomendacao, AcessoLivro, Instituicao

main = Blueprint('main', __name__)


@main.before_app_request
def criar_banco():
    from flask import current_app
    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    import os
    if not os.path.exists(db_path):
        db.create_all()


@main.route('/')
def home():
    return redirect(url_for('main.login'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(nome=nome, senha=senha).first()
        if usuario:
            session['usuario_id'] = usuario.id
            session['tipo'] = usuario.tipo
            return redirect(url_for('main.painel'))
        else:
            return render_template('login.html', erro="Usuário ou senha incorretos")
    return render_template('login.html')


@main.route('/logout')
def logout():
    session.pop('usuario_id', None)
    session.pop('tipo', None)
    return redirect(url_for('main.login'))


@main.route('/painel')
def painel():
    if 'usuario_id' not in session:
        return redirect(url_for('main.login'))

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

    return redirect(url_for('main.login'))


@main.route('/recomendar', methods=['POST'])
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
    return redirect(url_for('main.painel'))


@main.route('/baixar/<int:livro_id>')
def baixar_livro(livro_id):
    if 'usuario_id' not in session:
        return redirect(url_for('main.login'))
    acesso = AcessoLivro(
        usuario_id=session['usuario_id'],
        livro_id=livro_id,
        status='baixado',
        data=datetime.now()
    )
    db.session.add(acesso)
    db.session.commit()
    return redirect(url_for('main.painel'))


@main.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form['email']
        print(f"Recuperar senha para o email: {email}")
        return render_template('recuperar_senha_sucesso.html', email=email)
    return render_template('recuperar_senha.html')


@main.route('/cadastrar', methods=['GET', 'POST'])
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
        return redirect(url_for('main.login'))
    return render_template('cadastro.html')


# ROTAS EXTRAS PARA O PAINEL DO ADMINISTRADOR

@main.route('/salvar_instituicao', methods=['POST'])
def salvar_instituicao():
    if 'usuario_id' not in session or session['tipo'] != 'admin':
        return redirect(url_for('main.login'))

    nome = request.form['nome']
    telefone = request.form['telefone']
    email = request.form['email']

    instituicao = Instituicao.query.first()
    if not instituicao:
        instituicao = Instituicao(nome=nome, telefone=telefone, email=email)
        db.session.add(instituicao)
    else:
        instituicao.nome = nome
        instituicao.telefone = telefone
        instituicao.email = email

    db.session.commit()
    return redirect(url_for('main.painel'))


@main.route('/cadastrar_professor', methods=['POST'])
def cadastrar_professor():
    if 'usuario_id' not in session or session['tipo'] != 'admin':
        return redirect(url_for('main.login'))

    nome = request.form['nome']
    email = request.form['email']
    senha_padrao = '123456'
    tipo = 'professor'

    usuario_existente = Usuario.query.filter_by(email=email).first()
    if usuario_existente:
        return redirect(url_for('main.painel'))

    novo_professor = Usuario(nome=nome, email=email, senha=senha_padrao, tipo=tipo)
    db.session.add(novo_professor)
    db.session.commit()
    return redirect(url_for('main.painel'))


@main.route('/cadastrar_aluno', methods=['POST'])
def cadastrar_aluno():
    if 'usuario_id' not in session or session['tipo'] != 'admin':
        return redirect(url_for('main.login'))

    nome = request.form['nome']
    serie = request.form['serie']
    matricula = request.form['matricula']
    senha_padrao = '123456'
    tipo = 'aluno'

    aluno_existente = Usuario.query.filter_by(matricula=matricula).first()
    if aluno_existente:
        return redirect(url_for('main.painel'))

    novo_aluno = Usuario(nome=nome, serie=serie, matricula=matricula,
                         senha=senha_padrao, tipo=tipo)
    db.session.add(novo_aluno)
    db.session.commit()
    return redirect(url_for('main.painel'))
