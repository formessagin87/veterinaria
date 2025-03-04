from app import db

class Species(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    breeds = db.relationship('Breed', backref='species', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Species {self.name}>'