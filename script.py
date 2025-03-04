from sqlalchemy import text
from app import create_app, db

# Crear la aplicación
app = create_app()

# Ejecutar dentro del contexto de la aplicación
with app.app_context():
    with db.engine.connect() as connection:
        # Usar sqlalchemy.text() para eliminar la migración fallida
        query = text("DELETE FROM alembic_version WHERE version_num = 'fa6a2f57a136';")
        connection.execute(query)
        print("Migración eliminada del historial.")

