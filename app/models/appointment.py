from datetime import datetime, date
from app import db
from sqlalchemy import ForeignKey

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reason = db.Column(db.String(200), nullable=False)
    pet_id = db.Column(db.Integer, db.ForeignKey('pet.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f'<Appointment {self.date}>'