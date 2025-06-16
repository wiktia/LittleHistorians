from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "tajny_klucz_sesji"

# Konfiguracja bazy danych SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "game.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Kroki gry i ich przypisane ścieżki
steps = ['start', 'login', 'puzzle', 'text_to_image', 'timeline', 'end']
step_routes = {
    'start': 'startscreen',
    'login': 'logowanie',
    'puzzle': 'puzzle',
    'text_to_image': 'text_to_image',
    'timeline': 'timeline',
    'end': 'endscreen' 
}

# Model gracza
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    avatar = db.Column(db.String(120))
    score = db.Column(db.Integer, default=0)
    current_step = db.Column(db.String(50), default='start')


with app.app_context():
    db.create_all()


@app.route("/")
def startscreen():
    return render_template("startscreen.html")

@app.route("/logowanie")
def logowanie():
    return render_template("logowanie.html")

@app.route("/start", methods=["POST"])
def start():
    name = request.form.get("name")
    avatar = request.form.get("avatar")

    if not name or not avatar:
        return "Błąd: brak imienia lub avatara", 400

    player = Player(name=name, avatar=avatar, current_step='puzzle')
    db.session.add(player)
    db.session.commit()

    session["player_id"] = player.id
    return redirect(url_for("next_step"))

@app.route("/puzzle")
def puzzle():
    if "player_id" not in session:
        return redirect(url_for("logowanie"))
    return render_template("puzzle.html")

@app.route("/text_to_image")
def text_to_image():
    if "player_id" not in session:
        return redirect(url_for("logowanie"))
    return render_template("text_to_image.html")

@app.route("/timeline")
def timeline():
    if "player_id" not in session:
        return redirect(url_for("logowanie"))
    return render_template("timeline.html")

@app.route("/end")
def end_screen():
    return redirect(url_for("endscreen"))

@app.route("/endscreen")  
def endscreen():
    player_id = session.get("player_id")
    if not player_id:
        return redirect(url_for("logowanie"))

    player = Player.query.get(player_id)
    if not player:
        return "Gracz nie istnieje", 404

    return render_template("endscreen.html", player=player)

@app.route("/save_score", methods=["POST"])
def save_score():
    if "player_id" not in session:
        return jsonify({"error": "Brak dostępu – gracz nie zalogowany"}), 401

    data = request.get_json()
    score = int(data.get("score", 0))

    player = Player.query.get(session["player_id"])
    if not player:
        return jsonify({"error": "Gracz nie znaleziony"}), 404

    player.score += score
    player.current_step = get_next_step(player.current_step)  
    db.session.commit()
    print(f"Po aktualizacji: krok={player.current_step}, wynik={player.score}") 
    return jsonify({
        "message": "Wynik zapisany",
        "new_score": player.score,
        "next_step": player.current_step
    })

@app.route('/next')
def next_step():
    if 'player_id' not in session:
        return redirect(url_for('logowanie'))

    player = Player.query.get(session['player_id'])
    if not player:
        return redirect(url_for('logowanie'))

    next_step = player.current_step
    return redirect(url_for(step_routes.get(next_step, 'endscreen')))


def get_next_step(current):
    try:
        idx = steps.index(current)
        return steps[idx + 1] if idx + 1 < len(steps) else 'end'
    except ValueError:
        return 'end'

@app.route("/update_score", methods=["POST"])
def update_score():
    return save_score()  

if __name__ == "__main__":
    app.run(debug=True)
