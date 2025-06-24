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
class GameStep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_type = db.Column(db.String(50), nullable=False)  
    order = db.Column(db.Integer, nullable=False)        # Kolejność wyświetlania
    config = db.Column(db.JSON)                          
    is_active = db.Column(db.Boolean, default=True)      # Czy krok aktywny

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
    correct = db.Column(db.Integer, nullable=False)  


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    date = db.Column(db.String(10))   

# Utwórz tabele
with app.app_context():
    db.create_all()
    if not GameStep.query.first():
        default_steps = [
            GameStep(game_type='start', order=0, is_active=True),
            GameStep(game_type='login', order=1, is_active=True),
            GameStep(game_type='puzzle', order=2, is_active=True),
            GameStep(game_type='text_to_image', order=3, is_active=True),
            GameStep(game_type='timeline', order=4, is_active=True),
            GameStep(game_type='quiz', order=5, is_active=True),
            GameStep(game_type='end', order=6, is_active=True)
        ]
        db.session.add_all(default_steps)
        db.session.commit()    

# Funkcje pomocnicze
def get_all_steps():
    return [step.game_type for step in GameStep.query.order_by(GameStep.order).all()]

def get_next_step(current):
    active_steps = get_all_steps()  

    if current in active_steps:
        idx = active_steps.index(current)
        if idx + 1 < len(active_steps):
            return active_steps[idx + 1]
        return 'end'
    elif active_steps:
        return active_steps[0]
    return 'end'


def get_step_route(game_type):
    routes = {
        'start': 'startscreen',
        'login': 'logowanie',
        'puzzle': 'puzzle',
        'text_to_image': 'text_to_image',
        'timeline': 'timeline',
        'quiz': 'quiz',
        'end': 'endscreen'
    }
    return routes.get(game_type, 'end')  

# Panel administracyjny
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == 'maslo': #trzeba tu zmienić na jakieś szyfrowanie czy coś 
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Nieprawidłowe hasło', 'danger')
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    questions = QuizQuestion.query.all()
    return render_template('admin/dashboard.html', questions=questions)

@app.route('/admin/steps')
def manage_steps():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    steps = GameStep.query.order_by(GameStep.order).all()
    return render_template('admin/steps.html', steps=steps)

@app.route('/admin/step/edit/<int:id>', methods=['GET', 'POST'])
def edit_step(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    step = GameStep.query.get_or_404(id)
    if request.method == 'POST':
        step.game_type = request.form['game_type']
        step.order = int(request.form['order'])
        step.is_active = 'is_active' in request.form
        # Tutaj obsługa config jeśli potrzebujesz
        db.session.commit()
        flash('Krok zaktualizowany!', 'success')
        return redirect(url_for('manage_steps'))
    
    return render_template('admin/edit_step.html', step=step)
@app.route('/admin/step/add', methods=['GET', 'POST'])
def add_step():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        new_step = GameStep(
            game_type=request.form['game_type'],
            order=int(request.form['order']),
            is_active='is_active' in request.form,
            config={}  # Możesz dodać konfigurację jeśli potrzebujesz
        )
        db.session.add(new_step)
        db.session.commit()
        flash('Krok dodany pomyślnie!', 'success')
        return redirect(url_for('manage_steps'))
    
    return render_template('admin/add_step.html')

@app.route('/admin/step/delete/<int:id>', methods=['POST'])
def delete_step(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    step = GameStep.query.get_or_404(id)
    db.session.delete(step)
    db.session.commit()
    flash('Krok usunięty pomyślnie!', 'success')
    return redirect(url_for('manage_steps'))

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
    
    return render_template('admin/add_question.html')

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
    
    return render_template('admin/edit_question.html', question=question)

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


@app.route('/admin/timeline', methods=['GET', 'POST'])
def edit_timeline():
    # Pobierz istniejące wydarzenia lub stwórz domyślne jeśli brak
    timeline_events = Event.query.order_by(Event.date.desc()).limit(3).all()
    
    if request.method == 'POST':
        for i, event in enumerate(timeline_events):
            event.description = request.form.get(f'event_text_{i}')
            event.date = request.form.get(f'event_date_{i}')
        db.session.commit()
        flash("Zapisano zmiany!", "success")
        return redirect('/admin/timeline')

    return render_template('admin/edit_timeline.html', events=timeline_events)


# Główne endpointy gry
@app.route("/")
def startscreen():
    return render_template("startscreen.html")

@app.route("/logowanie")
def logowanie():
    return render_template("logowanie.html")

@app.route("/start", methods=["POST"])
def start():
    print(">>> [DEBUG start] sesja przed:", session)
    name = request.form.get("name")
    avatar = request.form.get("avatar")

    if not name or not avatar:
        flash("Proszę wypełnić wszystkie pola", "error")
        return redirect(url_for("logowanie"))

    # Znajdź lub stwórz gracza
    player = Player.query.filter_by(name=name, avatar=avatar).first()
    if not player:
        player = Player(name=name, avatar=avatar, score=0)
        db.session.add(player)

    player.current_step = 'login'
    db.session.commit()

    # ustawiamy sesję i od razu lecimy do puzzle
    session['player_id'] = player.id
    print(">>> [DEBUG start] sesja po:", session)
    return redirect(url_for('next_step'))


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

@app.route('/timeline')
def timeline():
    timeline_events = Event.query.order_by(Event.date.desc()).limit(3).all()

    events = timeline_events.copy()
    import random
    random.shuffle(events)

    return render_template('timeline.html',
                           events=events,
                           slot1_date=timeline_events[0].date,
                           slot2_date=timeline_events[1].date,
                           slot3_date=timeline_events[2].date)

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
    db.session.commit()
    
    return jsonify({
        "message": "Wynik zapisany",
        "new_score": player.score,
        "next_step_url": url_for("next_step")  
    })

@app.route("/next")
def next_step():
    if "player_id" not in session:
        return redirect(url_for("logowanie"))

    player = Player.query.get(session["player_id"])
    if not player:
        return redirect(url_for("logowanie"))

    # Pokaż ekran ładowania przed przejściem do następnego kroku
    return render_template("loading.html", next_step=get_next_step(player.current_step))
@app.route("/load_next_step")
def load_next_step():
    if "player_id" not in session:
        return redirect(url_for("logowanie"))

    player = Player.query.get(session["player_id"])
    if not player:
        return redirect(url_for("logowanie"))

    nxt = get_next_step(player.current_step)
    player.current_step = nxt
    db.session.commit()
    
    return redirect(url_for(get_step_route(nxt)))

@app.route("/update_score", methods=["POST"])
def update_score():
    return save_score()
<<<<<<< HEAD
=======
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
    return render_template('admin/ranking.html', players=players)
>>>>>>> b04f28fecdefd706d0d636e166a3f178ddc82395

if __name__ == "__main__":
    app.run(debug=True)