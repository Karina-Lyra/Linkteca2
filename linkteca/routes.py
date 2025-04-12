from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from datetime import datetime
from .models import db, Usuario, Livro, AcessoLivro, Comentario, TabelaAluno, Instituicao
from .utils import enviar_email

main = Blueprint('main', __name__)


@main.before_app_request
def criar_banco():
    import os
    from flask import current_app
    db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if not os.path.exists(db_path):
        db.create_all()


# Login
@main.route('/', methods=['GET', 'POST'])
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
            flash("Nome ou senha incorretos")
    return render_template('login.html')


# Logout
@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))


# Cadastro
@main.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        tipo = request.form['tipo']
        nome = request.form['nome']
        senha = request.form['senha']
        email = request.form.get('email')

        if tipo == 'professor':
            chave = request.form['chave']
            if chave != 'PROF123':
                flash("Chave de cadastro inválida.")
                return render_template('cadastro.html')
            novo_usuario = Usuario(nome=nome, senha=senha, tipo='professor', email=email)

        elif tipo == 'aluno':
            matricula = request.form['matricula']
            tabela = TabelaAluno.query.filter_by(nome=nome, matricula=matricula).first()
            if not tabela:
                flash("Aluno não encontrado na lista da instituição.")
                return render_template('cadastro.html')
            novo_usuario = Usuario(
                nome=nome, senha=senha, tipo='aluno',
                email=email, serie=tabela.serie,
                matricula=matricula, instituicao=tabela.instituicao
            )
        else:
            flash("Tipo inválido")
            return render_template('cadastro.html')

        db.session.add(novo_usuario)
        db.session.commit()
        flash("Cadastro realizado com sucesso")
        return redirect(url_for('main.login'))

    return render_template('cadastro.html')


# Painel
@main.route('/painel')
def painel():
    if 'usuario_id' not in session:
        return redirect(url_for('main.login'))
    usuario = Usuario.query.get(session['usuario_id'])

    if usuario.tipo == 'professor':
        return render_template('professor.html', usuario=usuario)
    elif usuario.tipo == 'aluno':
        livros = Livro.query.filter_by(serie=usuario.serie).all()
        return render_template('aluno.html', usuario=usuario, livros=livros)
    return redirect(url_for('main.login'))


# Página do livro
@main.route('/livro/<int:livro_id>', methods=['GET', 'POST'])
def livro(livro_id):
    livro = Livro.query.get_or_404(livro_id)
    comentarios = Comentario.query.filter_by(livro_id=livro.id).order_by(Comentario.data.desc()).all()

    if request.method == 'POST':
        if 'usuario_id' not in session:
            return redirect(url_for('main.login'))
        comentario = Comentario(
            usuario_id=session['usuario_id'],
            livro_id=livro_id,
            texto=request.form['comentario'],
            avaliacao=int(request.form['avaliacao']),
            data=datetime.now()
        )
        db.session.add(comentario)
        db.session.commit()
        return redirect(url_for('main.livro', livro_id=livro_id))

    return render_template('livro.html', livro=livro, comentarios=comentarios)


# Estatísticas
@main.route('/estatisticas')
def estatisticas():
    mais_baixados = Livro.query.order_by(Livro.downloads.desc()).limit(3).all()
    melhores_avaliados = Livro.query.order_by(Livro.media_avaliacao.desc()).limit(3).all()
    comentarios_recentes = Comentario.query.order_by(Comentario.data.desc()).limit(10).all()
    usuarios_ativos = Usuario.query.order_by(Usuario.atividade.desc()).limit(3).all()
    return render_template('estatisticas.html',
                           mais_baixados=mais_baixados,
                           melhores_avaliados=melhores_avaliados,
                           comentarios_recentes=comentarios_recentes,
                           usuarios_ativos=usuarios_ativos)


# Recuperar senha
@main.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        nome = request.form['nome']
        tipo = request.form['tipo']  # Novo campo: tipo de usuário
        email = request.form.get('email')
        usuario = Usuario.query.filter_by(nome=nome).first()

        if not usuario:
            flash("Usuário não encontrado.")
            return render_template('recuperar_senha.html')

        if tipo == 'aluno':
            if email:
                enviar_email(usuario.email, "Recuperação de Senha", f"Sua senha é: {usuario.senha}")
                flash("Senha enviada para seu email.")
            else:
                usuario.senha = usuario.matricula
                db.session.commit()
                flash("Senha redefinida para a matrícula.")
        elif tipo == 'professor':
            if usuario.email:
                enviar_email(usuario.email, "Recuperação de Senha", f"Sua senha é: {usuario.senha}")
                flash("Senha enviada para seu email.")
            else:
                flash("Professores precisam cadastrar um email para recuperar a senha.")
        else:
            flash("Tipo de usuário inválido.")

        return redirect(url_for('main.login'))

    return render_template('recuperar_senha.html')
