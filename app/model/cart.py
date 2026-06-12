from app.model.games import db, Game
import uuid
from datetime import datetime

#Μοντέλα Active Καλαθιών(προς επεξεργασία)
class Cart(db.Model):
    __tablename__ = 'carts'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship("CartItem", backref="cart", lazy=True, cascade="all, delete-orphan")

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cart_id = db.Column(db.String, db.ForeignKey('carts.id'), nullable=False)
    game_id = db.Column(db.String, db.ForeignKey('games.id'), nullable=False)
    game = db.relationship("Game")
    
#Μοντέλα Αγορασμένων Καλαθιών και Αντικειμένων
class PurchasedCart(db.Model):
    __tablename__ = 'purchased_carts'
    id = db.Column(db.String, primary_key=True)
    purchased_at = db.Column(db.DateTime, nullable=False)  # ❗ Remove default
    items = db.relationship(
        "PurchasedCartItem",
        backref="purchased_cart",
        lazy=True,
        cascade="all, delete-orphan"
    )

class PurchasedCartItem(db.Model):
    __tablename__ = 'purchased_cart_items'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    purchased_cart_id = db.Column(db.String, db.ForeignKey('purchased_carts.id'), nullable=False)
    game_id = db.Column(db.String, db.ForeignKey('games.id'), nullable=False)
    game = db.relationship("Game")