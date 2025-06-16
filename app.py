from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Konfiguracja bazy SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "game.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Model gracza
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    avatar = db.Column(db.String(120))
    score = db.Column(db.Integer, default=0)

# Utworzenie bazy danych
with app.app_context():
    db.create_all()

# 🔹 Startscreen
@app.route("/")
def startscreen():
    return render_template("startscreen.html")

# 🔹 Logowanie formularz
@app.route("/logowanie")
def logowanie():
    return render_template("logowanie.html")

# 🔹 Obsługa formularza logowania
@app.route("/start", methods=["POST"])
def start():
    name = request.form.get("name")
    avatar = request.form.get("avatar")

    if not name or not avatar:
        return "Błąd: brak imienia lub avatara", 400

    player = Player(name=name, avatar=avatar)
    db.session.add(player)
    db.session.commit()

    # 🔹 Na potrzeby testów od razu przekierowujemy na endscreen
    return redirect(url_for("endscreen", player_id=player.id))

@app.route("/endscreen")
def endscreen():
    player_id = request.args.get("player_id")
    player = Player.query.get(player_id)
    if not player:
        return "Gracz nie istnieje", 404
    return render_template("endscreen.html", player=player)
    
@app.route("/quiz")
def quiz():
    player_id = request.args.get("player_id")
    return render_template("quiz.html", player_id=player_id)

@app.route("/update_score", methods=["POST"])
def update_score():
    player_id = request.form.get("player_id")
    score = int(request.form.get("score"))
    player = Player.query.get(player_id)
    if player:
        player.score += score
        db.session.commit()
        return "OK"
    return "Player not found", 404

if __name__ == "__main__":
    app.run(debug=True)
