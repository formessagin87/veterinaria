from app import create_app, db
from app.models.user import User

# Inicializar la app y el contexto
app = create_app()
app.app_context().push()

# Solicitar datos al usuario
username = input("Username: ")
email = input("Email: ")
password = input("Password: ")
role = input("Role (admin/user/etc.): ")

# Crear y configurar el usuario
new_user = User(username=username, email=email, role=role)
new_user.set_password(password)  # 🔐 Esto es lo más importante

# Guardar en la base de datos
db.session.add(new_user)
db.session.commit()

print(f"✅ Usuario '{username}' creado correctamente.")
