# test_login.py

from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # Paso 1: Buscar usuario, eliminar si ya existe
    user = User.query.filter_by(username='admin').first()
    if user:
        db.session.delete(user)
        db.session.commit()
        print("🔄 Usuario 'admin' eliminado.")

    # Paso 2: Crear usuario nuevo
    user = User(username='admin', email='admin@test.com', role='admin')
    user.set_password('admin')
    db.session.add(user)
    db.session.commit()
    print("✅ Usuario 'admin' creado con contraseña 'admin'.")

    # Paso 3: Buscarlo nuevamente
    user = User.query.filter_by(username='admin').first()
    if user:
        print(f"👀 Usuario encontrado: {user.username}")
        print(f"🔑 Password Hash: {user.password_hash}")
        result = user.check_password('admin')
        print(f"✅ ¿Contraseña correcta?: {result}")
    else:
        print("❌ No se encontró el usuario.")
