from datetime import datetime, date
from app import db
from sqlalchemy import ForeignKey

class Pet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    observations = db.Column(db.Text, nullable=True)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id'), nullable=False)
    breed_id = db.Column(db.Integer, db.ForeignKey('breed.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('owner.id'), nullable=False)
    
    medical_records = db.relationship('MedicalRecord', backref='pet', lazy=True)
    appointments = db.relationship('Appointment', backref='pet', lazy=True)
    
    # Relaciones
    species = db.relationship('Species', backref='pets', lazy=True)
    breed = db.relationship('Breed', backref='pets', lazy=True)
    
    def calculate_age(self):
        """Calcula la edad a partir de la fecha de nacimiento."""
        today = date.today()
        age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return age
    
    def __repr__(self):
        return f'<Pet {self.name}>'