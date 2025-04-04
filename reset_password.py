from app import create_app, db
from app.models.user import User

# Inicializa la app (si usas Factory Pattern)
app = create_app()

with app.app_context():
    username = input("Ingrese el nombre de usuario: ")
    new_password = input("Ingrese la nueva contraseña: ")

    user = User.query.filter_by(username=username).first()

    if user:
        user.set_password(new_password)
        db.session.commit()
        print(f"✅ Contraseña actualizada para el usuario '{username}'.")
    else:
        print(f"❌ No se encontró un usuario con el nombre '{username}'.")
