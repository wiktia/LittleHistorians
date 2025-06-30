from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import os
from datetime import datetime

from models import db, GameStep, Player, QuizQuestion, Timeline, TimelineEvent

from admin import admin_bp


app = Flask(__name__)
app.secret_key = "tajny_klucz_sesji"
app.register_blueprint(admin_bp)

# Konfiguracja bazy danych SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "game.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# Funkcje pomocnicze
def get_all_steps():
    return [step.game_type for step in GameStep.query.order_by(GameStep.order).all()]

def get_next_step(current_identifier):
    current_step = GameStep.query.filter_by(step_identifier=current_identifier).first()
    if not current_step:
        return 'end'
    
    # Pobierz następny aktywny krok
    next_step = GameStep.query.filter(
        GameStep.order > current_step.order,
        GameStep.is_active == True
    ).order_by(GameStep.order).first()
    
    return next_step.step_identifier if next_step else 'end'

def get_step_route(step_identifier):
    # Wydziel typ gry z identyfikatora (np. "quiz-1" → "quiz")
    game_type = step_identifier.split('-')[0] if '-' in step_identifier else step_identifier
    
    routes = {
        'start': 'startscreen',
        'login': 'logowanie',
        'quiz': 'quiz',
        'puzzle': 'puzzle',
        'text_to_image': 'text_to_image',
        'timeline': 'timeline',
        'end': 'endscreen'
    }
    return routes.get(game_type, 'endscreen')

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

@app.route('/api/quiz_question_by_step')
def get_quiz_question_by_step():
    step = request.args.get('step')
    if not step or not step.startswith('quiz-'):
        return jsonify({"error": "Nieprawidłowy parametr step"}), 400
    
    try:
        question_id = int(step.split('-')[1])
    except (IndexError, ValueError):
        return jsonify({"error": "Nieprawidłowy format step"}), 400
    
    question = QuizQuestion.query.get(question_id)
    if not question:
        return jsonify([])  # brak pytania - koniec quizu
    
    answers = [question.answer1, question.answer2]
    if question.answer3:
        answers.append(question.answer3)
    if question.answer4:
        answers.append(question.answer4)
    
    return jsonify([{
        'id': question.id,
        'question': question.question,
        'answers': answers,
        'correct': question.correct
    }])

# API dla timeline'ów
@app.route('/api/timeline_events')
def get_timeline_events():
    timeline_id = request.args.get('timeline_id')
    if not timeline_id:
        return jsonify([])
    
    timeline_db_id = get_timeline_id(timeline_id)
    if not timeline_db_id:
        return jsonify([])
    
    events = TimelineEvent.query.filter_by(timeline_id=timeline_db_id).order_by(TimelineEvent.order).all()
    
    return jsonify([{
        'id': e.id,
        'title': e.title,
        'description': e.description,
        'year': e.year
    } for e in events])

@app.route('/api/timeline_correct_order')
def get_timeline_correct_order():
    timeline_id = request.args.get('timeline_id')
    if not timeline_id:
        return jsonify([])
    
    timeline_db_id = get_timeline_id(timeline_id)
    if not timeline_db_id:
        return jsonify([])
    
    events = TimelineEvent.query.filter_by(timeline_id=timeline_db_id).order_by(TimelineEvent.order).all()
    return jsonify([e.year for e in events])

@app.route("/update_timeline_score", methods=["POST"])
def update_timeline_score():
    if "player_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.get_json()
    timeline_id = data.get("timeline_id")
    score = data.get("score")
    
    player = Player.query.get(session["player_id"])
    if player:
        player.score += int(score)
        db.session.commit()
        return jsonify({"success": True})
    
    return jsonify({"error": "Player not found"}), 404

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
        flash("Proszę wypełnić wszystkie pola", "error")
        return redirect(url_for("logowanie"))

    # Wyciągnij czysty numer awatara (np. "1.png" -> "1")
    avatar_number = os.path.splitext(avatar)[0]
    
    # Zapisz tylko numer awatara w sesji
    session['avatar'] = avatar_number

    player = Player.query.filter_by(name=name, avatar=avatar).first()
    if not player:
        player = Player(name=name, avatar=avatar, score=0)
        db.session.add(player)

    player.start_time = datetime.now()
    player.current_step = 'login'
    db.session.commit()

    session['player_id'] = player.id
    return redirect(url_for('next_step'))
@app.route("/api/get_start_time")
def get_start_time():
    if "player_id" not in session:
        return jsonify({"error": "Brak dostępu"}), 401

    player = Player.query.get(session["player_id"])
    if not player:
        return jsonify({"error": "Gracz nie znaleziony"}), 404

    # Upewnij się, że czas startu istnieje
    if not player.start_time:
        player.start_time = datetime.now()
        db.session.commit()

    return jsonify({
        "start_time": player.start_time.isoformat()
    })

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

def get_timeline_id(identifier):
    if identifier.isdigit():
        return int(identifier)
    
    timeline = Timeline.query.filter_by(identifier=identifier).first()
    return timeline.id if timeline else None  # zwróć None zamiast 1

    
    
@app.route('/timeline')
def timeline():
    if "player_id" not in session:
        print("Redirecting to login: no player_id in session")
        return redirect(url_for("logowanie"))
    
    timeline_id = request.args.get('timeline_id')
    print(f"Requested timeline_id: {timeline_id}")
    
    # Sprawdź czy gracz już ukończył tę oś
    completion_key = f"completed_{timeline_id}"
    print(f"Checking completion key: {completion_key}")
    if completion_key in session:
        print(f"Timeline {timeline_id} already completed. Redirecting to next_step.")
        return redirect(url_for('next_step'))
    
    # Pobierz ID osi czasu w bazie
    timeline_db_id = get_timeline_id(timeline_id)
    print(f"Database timeline ID: {timeline_db_id}")
    
    if not timeline_db_id:
        print(f"Timeline not found for identifier: {timeline_id}")
        flash("Nie znaleziono osi czasu", "error")
        return redirect(url_for('next_step'))
    
    # Pobierz wydarzenia
    events = TimelineEvent.query.filter_by(timeline_id=timeline_db_id).order_by(TimelineEvent.order).limit(3).all()
    print(f"Found {len(events)} events for timeline {timeline_id}")
    
    # Sprawdź czy są wystarczająco wydarzeń
    if len(events) < 3:
        print(f"Not enough events ({len(events)}) for timeline {timeline_id}")
        flash("Ta oś czasu nie ma wystarczającej liczby wydarzeń", "error")
        return redirect(url_for('next_step'))
    
    # Zapisz w sesji, że oś została ukończona
    session[completion_key] = True
    print(f"Marked timeline {timeline_id} as completed")
    
    return render_template('timeline.html', 
                         events=events,
                         timeline_id=timeline_id,
                         slot1_year=events[0].year,
                         slot2_year=events[1].year,
                         slot3_year=events[2].year)
@app.route("/quiz")
def quiz():
    if "player_id" not in session:
        return redirect(url_for("logowanie"))
    return render_template("quiz.html")

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

    return render_template("endscreen.html", player=player, rank=rank)

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

@app.route('/next')
def next_step():
    if "player_id" not in session:
        return redirect(url_for("logowanie"))

    player = Player.query.get(session['player_id'])
    
    # Standardowa obsługa następnego kroku
    next_step_identifier = get_next_step(player.current_step)

    # Get the image index from the current step (if applicable)
    image_index = None
    if player.current_step and '-' in player.current_step:
        try:
            image_index = player.current_step.split('-')[1]
        except:
            pass
    
    # Update player's current step in database
    player.current_step = next_step_identifier
    db.session.commit()
    
    # Redirect to animation screen first
    return redirect(url_for('loading_screen', next_step=next_step_identifier, image_index=image_index))

@app.route('/loading_screen')
def loading_screen():
    next_step = request.args.get('next_step')
    
    # Pobierz numer awatara z sesji
    avatar_number = session.get('avatar', '')
    
    # Utwórz ścieżkę do obrazka z dopiskiem -like
    if avatar_number and avatar_number.isdigit() and 1 <= int(avatar_number) <= 23 and int(avatar_number) % 2 != 0:
        image_path = f"static/obrazki/{avatar_number}-like.png"
    else:
        image_path = None
    
    return render_template('animationpositive.html', 
                        next_step_url=url_for(get_step_route(next_step)),
                        image_path=image_path)


if __name__ == "__main__":
    app.run(debug=True)





    