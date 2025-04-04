from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from sqlalchemy import event
from sqlalchemy.engine import Engine
from flask_login import LoginManager, current_user
from sqlalchemy import MetaData
from functools import wraps
from flask import abort


# from app.models.user import User

# (Opcional) Definir una convención de nombres para restricciones
naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=naming_convention)
db = SQLAlchemy(metadata=metadata)
# Crea la instancia del gestor de login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
migrate = Migrate()
mail = Mail()

def roles_required(*roles):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)  # Prohibido si no está autenticado
            if current_user.role not in roles:
                abort(403)  # Prohibido si el rol no es el esperado
            return func(*args, **kwargs)
        return wrapped
    return decorator

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    
    from app.models.config import ClinicConfig

    from app.routes import main
    app.register_blueprint(main)

    from app.auth.routes import auth
    app.register_blueprint(auth, url_prefix='/auth')

    # 👇 Mover esto dentro de la función
    @app.context_processor
    def inject_clinic_config():
        config = ClinicConfig.query.first()
        return dict(config=config)

    return app
