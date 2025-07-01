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
       
    # Standardowe wyszukiwanie następnego kroku
    next_step = GameStep.query.filter(
        GameStep.order > current_step.order,
        GameStep.is_active == True,
        ~GameStep.step_identifier.in_(['start', 'login'])
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
@app.route('/api/timelines')
def get_timelines():
    timelines = Timeline.query.order_by(Timeline.order).all()
    return jsonify([{
        'id': t.id,
        'identifier': t.identifier,
        'title': t.title,
        'description': t.description,
        'is_active': t.is_active
    } for t in timelines])

@app.route('/api/timeline_events')
def get_timeline_events():
    timeline_id = request.args.get('timeline_id')
    if not timeline_id:
        return jsonify({'error': 'Brak parametru timeline_id'}), 400
    
    # Możliwe jest przekazanie ID jako number (1) lub identifier (timeline-1)
    if timeline_id.isdigit():
        events = TimelineEvent.query.filter_by(timeline_id=timeline_id).order_by(TimelineEvent.order).all()
    else:
        timeline = Timeline.query.filter_by(identifier=timeline_id).first()
        if not timeline:
            return jsonify({'error': 'Nie znaleziono osi czasu'}), 404
        events = timeline.events.order_by(TimelineEvent.order).all()
    
    return jsonify([{
        'id': e.id,
        'title': e.title,
        'description': e.description,
        'date': e.date,
        'image_url': e.image_url
    } for e in events])

@app.route('/api/timeline_correct_order')
def get_timeline_correct_order():
    timeline_id = request.args.get('timeline_id')
    if not timeline_id:
        return jsonify({'error': 'Brak parametru timeline_id'}), 400
    
    if timeline_id.isdigit():
        events = TimelineEvent.query.filter_by(timeline_id=timeline_id).order_by(TimelineEvent.order).all()
    else:
        timeline = Timeline.query.filter_by(identifier=timeline_id).first()
        if not timeline:
            return jsonify({'error': 'Nie znaleziono osi czasu'}), 404
        events = timeline.events.order_by(TimelineEvent.order).all()
    
    return jsonify([e.date for e in events])
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
    
    # Zapisz numer awatara w sesji jako liczbę
    session['avatar'] = int(avatar_number) if avatar_number.isdigit() else None

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
    # If no identifier provided, default to first timeline
    if identifier is None:
        timeline = Timeline.query.order_by(Timeline.order).first()
        return timeline.id if timeline else 1
    
    # If identifier is not a digit, find matching timeline
    if not identifier.isdigit():
        timeline = Timeline.query.filter_by(identifier=identifier).first()
        return timeline.id if timeline else 1  # default to first timeline
    
    return int(identifier)

@app.route('/timeline')
def timeline():
    if "player_id" not in session:
        return redirect(url_for("logowanie"))
    
    # Get timeline ID from URL (default to None if not provided)
    timeline_id = request.args.get('timeline_id')
    
    # Get 3 events from database
    events = TimelineEvent.query.filter_by(timeline_id=get_timeline_id(timeline_id)).order_by(TimelineEvent.order).limit(3).all()
    
    return render_template('timeline.html', 
                         events=events,
                         timeline_id=timeline_id or 'default')
    

@app.route("/quiz")
def quiz():
    if "player_id" not in session:
        return redirect(url_for("logowanie"))
    return render_template("quiz.html")

@app.route("/endscreen")  
def endscreen():
    avatar_number = session.get('avatar')
    player_id = session.get("player_id")
    if not player_id:
        return redirect(url_for("logowanie"))

    player = Player.query.get(player_id)
    if not player:
        return "Gracz nie istnieje", 404
    
    players = Player.query.order_by(Player.score.desc()).all()
    rank = next((index + 1 for index, p in enumerate(players) if p.id == player.id), None)
    image_path = f"obrazki/{avatar_number}.png"

    return render_template("endscreen.html", player=player, rank=rank, image_path=image_path)

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
    avatar_number = session.get('avatar')
    
    # Sprawdź czy avatar_number jest liczbą nieparzystą w zakresie 1-23
    if isinstance(avatar_number, int) and 1 <= avatar_number <= 23 and avatar_number % 2 != 0:
        image_path = f"obrazki/{avatar_number}-like.png"
    else:
        image_path = None
    print(f"Avatar number in session: {session.get('avatar')}")
    return render_template('animationpositive.html', 
                        next_step_url=url_for(get_step_route(next_step)),
                        image_path=image_path)

if __name__ == "__main__":
    app.run(debug=True)





    