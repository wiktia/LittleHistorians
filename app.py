from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Konfiguracja bazy danych SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODEL: użytkownik
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pseudonim = db.Column(db.String(80), nullable=False)
    awatar = db.Column(db.String(120))  # np. link lub nazwa pliku
    wynik = db.Column(db.Integer, default=0)

# Tworzenie tabel
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    pseudonim = request.form.get('pseudonim')
    if pseudonim:
        new_user = User(pseudonim=pseudonim)
        db.session.add(new_user)
        db.session.commit()
        return f"Dziękujemy, {pseudonim}! Zapisano do bazy danych."
    return "Nie podano pseudonimu!", 400

if __name__ == '__main__':
    app.run(debug=True)
