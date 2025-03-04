from app import create_app, db
from app.models.user import User  # Asegúrate de que el modelo User esté bien importado
from werkzeug.security import generate_password_hash

def reset_password(username_or_email, new_password):
    """Restablece la contraseña de un usuario."""
    app = create_app()
    with app.app_context():
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        
        if user:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            print(f"✅ Contraseña de {user.username} restablecida correctamente.")
        else:
            print("⚠️ Usuario no encontrado.")

if __name__ == "__main__":
    username_or_email = input("Ingrese el nombre de usuario o email del usuario: ")
    new_password = input("Ingrese la nueva contraseña: ")
    reset_password(username_or_email, new_password)
