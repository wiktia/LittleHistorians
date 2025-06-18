from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "tajny_klucz_sesji"

# Konfiguracja bazy danych SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "game.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Modele
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    avatar = db.Column(db.String(120))
    score = db.Column(db.Integer, default=0)
    current_step = db.Column(db.String(50), default='start')

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer1 = db.Column(db.String(200), nullable=False)
    answer2 = db.Column(db.String(200), nullable=False)
    answer3 = db.Column(db.String(200))
    answer4 = db.Column(db.String(200))
    correct = db.Column(db.Integer, nullable=False)  # 1,2,3,4 - numer poprawnej odpowiedzi

# Utwórz tabele
with app.app_context():
    db.create_all()

# Kroki gry i ich przypisane ścieżki
steps = ['start', 'login', 'puzzle', 'text_to_image', 'timeline', 'quiz', 'end']
step_routes = {
    'start': 'startscreen',
    'login': 'logowanie',
    'puzzle': 'puzzle',
    'text_to_image': 'text_to_image',
    'timeline': 'timeline',
    'quiz': 'quiz',
    'end': 'endscreen' 
}

# Funkcje pomocnicze
def get_next_step(current):
    try:
        idx = steps.index(current)
        return steps[idx + 1] if idx + 1 < len(steps) else 'end'
    except ValueError:
        return 'end'

# Panel administracyjny
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == 'maslo': #trzeba tu zmienić na jakieś szyfrowanie czy coś 
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Nieprawidłowe hasło', 'danger')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    questions = QuizQuestion.query.all()
    return render_template('admin_dashboard.html', questions=questions)

@app.route('/admin/question/add', methods=['GET', 'POST'])
def add_question():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        new_question = QuizQuestion(
            question=request.form['question'],
            answer1=request.form['answer1'],
            answer2=request.form['answer2'],
            answer3=request.form.get('answer3', None),
            answer4=request.form.get('answer4', None),
            correct=int(request.form['correct'])
        )
        db.session.add(new_question)
        db.session.commit()
        flash('Pytanie dodane pomyślnie!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_question.html')

@app.route('/admin/question/edit/<int:id>', methods=['GET', 'POST'])
def edit_question(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    question = QuizQuestion.query.get_or_404(id)
    
    if request.method == 'POST':
        question.question = request.form['question']
        question.answer1 = request.form['answer1']
        question.answer2 = request.form['answer2']
        question.answer3 = request.form.get('answer3', None)
        question.answer4 = request.form.get('answer4', None)
        question.correct = int(request.form['correct'])
        db.session.commit()
        flash('Pytanie zaktualizowane pomyślnie!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_question.html', question=question)

@app.route('/admin/question/delete/<int:id>', methods=['POST'])
def delete_question(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    question = QuizQuestion.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    flash('Pytanie usunięte pomyślnie!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# API dla quizu
@app.route('/api/quiz_questions')
def get_quiz_questions():
    questions = QuizQuestion.query.all()
    output = []
    for q in questions:
        answers = [q.answer1, q.answer2]
        if q.answer3:
            answers.append(q.answer3)
        if q.answer4:
            answers.append(q.answer4)
            
        output.append({
            'id': q.id,
            'question': q.question,
            'answers': answers,
            'correct': q.correct
        })
    return jsonify(output)

# Główne endpointy gry
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

@app.route("/quiz")
def quiz():
    if "player_id" not in session:
        return redirect(url_for("logowanie"))
    return render_template("quiz.html")

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
    
    players = Player.query.order_by(Player.score.desc()).all()

    
    rank = next((index + 1 for index, p in enumerate(players) if p.id == player.id), None)

    return render_template("endscreen.html", player=player,  rank=rank)

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

@app.route("/update_score", methods=["POST"])
def update_score():
    return save_score()
@app.route("/admin/data")
def show_data():
    if not session.get('admin_logged_in'):
        return jsonify({"error": "Brak dostępu"}), 403

    players = Player.query.all()
    questions = QuizQuestion.query.all()

    return jsonify({
        "players": [
            {
                "id": p.id,
                "name": p.name,
                "avatar": p.avatar,
                "score": p.score,
                "current_step": p.current_step
            } for p in players
        ],
        "questions": [
            {
                "id": q.id,
                "question": q.question,
                "answer1": q.answer1,
                "answer2": q.answer2,
                "answer3": q.answer3,
                "answer4": q.answer4,
                "correct": q.correct
            } for q in questions
        ]
    })
@app.route('/admin/clear_players', methods=['POST'])
def clear_players():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    Player.query.delete()
    db.session.commit()
    flash('Wszyscy gracze zostali usunięci.', 'warning')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/ranking')
def admin_ranking():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    players = Player.query.order_by(Player.score.desc()).all()
    return render_template('admin_ranking.html', players=players)

if __name__ == "__main__":
    app.run(debug=True)

