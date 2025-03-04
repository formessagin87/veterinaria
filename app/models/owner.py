from app import db

class Owner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=True)

    pets = db.relationship('Pet', backref='owner', lazy=True)
    
    @staticmethod
    def search(query):
        return Owner.query.filter(
            Owner.name.contains(query) |
            Owner.phone.contains(query) |
            Owner.email.contains(query)
        ).all()
    
    def __repr__(self):
        return f'<Owner {self.name}>'