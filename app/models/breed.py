from app import db
from sqlalchemy import ForeignKey

class Breed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    species_id = db.Column(db.Integer, db.ForeignKey('species.id', ondelete='CASCADE', name='fk_breed_species'), nullable=False)

    def __repr__(self):
        return f'<Breed {self.name}>'
