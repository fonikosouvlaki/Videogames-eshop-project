from flask import Flask

server = Flask(__name__) # Δημιουργία της Flask εφαρμογής
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///games.db' # Ρύθμιση της βάσης δεδομένων SQLite
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Απενεργοποίηση παρακολούθησης αλλαγών για βελτίωση απόδοσης

from app.model.games import db # Εισαγωγή του αντικειμένου βάσης δεδομένων από το μοντέλο Game
db.init_app(server) # Σύνδεση της βάσης δεδομένων με την εφαρμογή Flask

with server.app_context(): # Δημιουργία των πινάκων της βάσης αν δεν υπάρχουν ήδη
    db.create_all()

from app import routes
from app import groq