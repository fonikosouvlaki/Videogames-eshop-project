from app import server
from flask_sqlalchemy import SQLAlchemy
import uuid
#ΒΔ
db = SQLAlchemy()

#Αντικείμενο Βιντεοπαιχνίδι
class Game(db.Model):
    __tablename__ = "games"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String, nullable=False)
    platform = db.Column(db.String, nullable=False)
    genre = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "platform": self.platform,
            "genre": self.genre,
            "price": self.price,
                "description": self.description,
            "image_url": self.image_url
        }

    def from_dict(self, data):
        for field in ['title', 'platform', 'genre', 'price', 'description', 'image_url']:
            if field in data:
                setattr(self, field, data[field])