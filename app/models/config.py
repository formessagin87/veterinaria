from app import db

class ClinicConfig(db.Model):
    __tablename__ = 'clinic_config'

    id = db.Column(db.Integer, primary_key=True)
    clinic_name = db.Column(db.String(100), nullable=False)
    logo_url = db.Column(db.String(255), nullable=True)
    primary_color = db.Column(db.String(7), nullable=True)
    secondary_color = db.Column(db.String(7), nullable=True)
    welcome_message = db.Column(db.String(255), nullable=True)
