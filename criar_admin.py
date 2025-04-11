from app import app, db
from models import Usuario  # ajuste conforme a localização real do modelo

with app.app_context():
    # Verificar se já existe um admin
    admin_existente = Usuario.query.filter_by(tipo='admin').first()

    if not admin_existente:
        admin = Usuario(
            nome='Administrador',
            senha='admin123',  # Lembre-se de trocar depois por algo mais seguro!
            tipo='admin',
            email='admin@linkteca.com'  # ou um valor válido se o campo for obrigatório
        )
        db.session.add(admin)
        db.session.commit()
        print("Administrador criado com sucesso!")
    else:
        print("Já existe um administrador cadastrado.")