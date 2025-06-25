from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
import os
import random
from datetime import datetime

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
    name = db.Column(db.String(50), nullable=False)  
    game_type = db.Column(db.String(50), nullable=False)  
    step_identifier = db.Column(db.String(50))  
    order = db.Column(db.Integer, nullable=False)  
    config = db.Column(db.JSON)  
    is_active = db.Column(db.Boolean, default=True)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    avatar = db.Column(db.String(120))
    score = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime, default=datetime.now)
    current_step = db.Column(db.String(50), default='start')  
    

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer1 = db.Column(db.String(200), nullable=False)
    answer2 = db.Column(db.String(200), nullable=False)
    answer3 = db.Column(db.String(200))
    answer4 = db.Column(db.String(200))
    correct = db.Column(db.Integer, nullable=False)  

class Timeline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(50), unique=True)  # np. timeline-1, timeline-2
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer)

class TimelineEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timeline_id = db.Column(db.Integer, db.ForeignKey('timeline.id'))
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    date = db.Column(db.String(50))  # format daty dostosowany do potrzeb
    image_url = db.Column(db.String(255))
    order = db.Column(db.Integer)  # kolejność w osi czasu

    timeline = db.relationship('Timeline', backref='events')

# Utwórz tabele i inicjalizuj dane
with app.app_context():
    db.create_all()

    # Inicjalizacja timeline'ów jeśli brak
    if not Timeline.query.first():
        default_timelines = [
            Timeline(identifier='timeline-1', title='Oś czasu 1', description='Pierwsza oś czasu', order=1, is_active=True),
            Timeline(identifier='timeline-2', title='Oś czasu 2', description='Druga oś czasu', order=2, is_active=True)
        ]
        db.session.add_all(default_timelines)
        db.session.commit()

        # Domyślne wydarzenia dla timeline-1
        timeline1 = Timeline.query.filter_by(identifier='timeline-1').first()
        if timeline1:
            events = [
                TimelineEvent(timeline_id=timeline1.id, title='Wydarzenie 1', description='Opis wydarzenia 1', date='1900', order=1),
                TimelineEvent(timeline_id=timeline1.id, title='Wydarzenie 2', description='Opis wydarzenia 2', date='1950', order=2),
                TimelineEvent(timeline_id=timeline1.id, title='Wydarzenie 3', description='Opis wydarzenia 3', date='2000', order=3)
            ]
            db.session.add_all(events)
        
        # Domyślne wydarzenia dla timeline-2
        timeline2 = Timeline.query.filter_by(identifier='timeline-2').first()
        if timeline2:
            events = [
                TimelineEvent(timeline_id=timeline2.id, title='Wydarzenie A', description='Opis wydarzenia A', date='1800', order=1),
                TimelineEvent(timeline_id=timeline2.id, title='Wydarzenie B', description='Opis wydarzenia B', date='1850', order=2),
                TimelineEvent(timeline_id=timeline2.id, title='Wydarzenie C', description='Opis wydarzenia C', date='1900', order=3)
            ]
            db.session.add_all(events)
        
        db.session.commit()
    
    if not GameStep.query.first():
        # Stałe kroki (nieusuwalne)
        fixed_steps = [
            GameStep(name="Start", game_type='start', step_identifier='start', order=0, is_active=True),
            GameStep(name="Logowanie", game_type='login', step_identifier='login', order=1, is_active=True),
            GameStep(name="Koniec", game_type='end', step_identifier='end', order=100, is_active=True)
        ]
        
        # Przykładowe kroki gier (można modyfikować)
        game_steps = [
            GameStep(name="Quiz 1", game_type='quiz', step_identifier='quiz-1', order=2, is_active=True),
            GameStep(name="Puzzle 1", game_type='puzzle', step_identifier='puzzle-1', order=3, is_active=True),
            GameStep(name="Tekst na obraz", game_type='text_to_image', step_identifier='text_to_image-1', order=4, is_active=True),
            GameStep(name="Oś czasu 1", game_type='timeline', step_identifier='timeline-1', order=5, is_active=True),
            GameStep(name="Oś czasu 2", game_type='timeline', step_identifier='timeline-2', order=6, is_active=True)
        ]
        
        db.session.add_all(fixed_steps + game_steps)
        db.session.commit()

# Funkcje pomocnicze
def get_all_steps():
    return [step.game_type for step in GameStep.query.order_by(GameStep.order).all()]

def get_next_step(current_identifier):
    current_step = GameStep.query.filter_by(step_identifier=current_identifier).first()
    if not current_step:
        return 'end'
    
    # Jeśli aktualny krok to timeline, sprawdź czy jest następny timeline
    if current_identifier.startswith('timeline'):
        current_timeline_id = current_identifier
        current_timeline = Timeline.query.filter_by(identifier=current_timeline_id).first()
        
        if current_timeline:
            next_timeline = Timeline.query.filter(
                Timeline.order > current_timeline.order,
                Timeline.is_active == True
            ).order_by(Timeline.order).first()
            
            if next_timeline:
                return next_timeline.identifier
    
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

# Panel administracyjny
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == 'maslo': # TODO: zmienić na bezpieczne hasło
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
    timelines = Timeline.query.count()
    return render_template('admin/dashboard.html', questions=questions, timelines=timelines)

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
        db.session.commit()
        flash('Krok zaktualizowany!', 'success')
        return redirect(url_for('manage_steps'))
    
    return render_template('admin/edit_step.html', step=step)

@app.route('/admin/step/add', methods=['GET', 'POST'])
def add_step():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        game_type = request.form['game_type']
        step_number = request.form['step_number']
        step_identifier = f"{game_type}-{step_number}"
        
        if GameStep.query.filter_by(step_identifier=step_identifier).first():
            flash('Krok o tym identyfikatorze już istnieje!', 'danger')
            return redirect(url_for('add_step'))
        
        try:
            order = int(request.form['order'])
        except ValueError:
            flash('Pole "order" musi być liczbą całkowitą!', 'danger')
            return redirect(url_for('add_step'))
        
        new_step = GameStep(
            name=f"{game_type.capitalize()} {step_number}",
            game_type=game_type,
            step_identifier=step_identifier,
            order=order,
            is_active='is_active' in request.form,
            config={}
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
    
    # Zabezpieczenie przed usunięciem stałych kroków
    if step.step_identifier in ['start', 'login', 'end']:
        flash('Nie można usunąć stałego kroku gry!', 'danger')
        return redirect(url_for('manage_steps'))
    
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

# Timeline management
@app.route('/admin/timelines')
def manage_timelines():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    timelines = Timeline.query.order_by(Timeline.order).all()
    return render_template('admin/timelines.html', timelines=timelines)

@app.route('/admin/timeline/<string:identifier>', methods=['GET', 'POST'])
def edit_timeline(identifier):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    timeline = Timeline.query.filter_by(identifier=identifier).first_or_404()
    
    if request.method == 'POST':
        timeline.title = request.form.get('title')
        timeline.description = request.form.get('description')
        timeline.is_active = 'is_active' in request.form
        
        # Aktualizacja wydarzeń
        for event in timeline.events:
            event.title = request.form.get(f'event_title_{event.id}')
            event.description = request.form.get(f'event_description_{event.id}')
            event.date = request.form.get(f'event_date_{event.id}')
            event.order = int(request.form.get(f'event_order_{event.id}', 0))
        
        db.session.commit()
        flash('Oś czasu zaktualizowana!', 'success')
        return redirect(url_for('manage_timelines'))
    
    return render_template('admin/edit_timeline.html', timeline=timeline)
    
@app.route('/admin/timeline/add', methods=['GET', 'POST'])
def add_timeline():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        if Timeline.query.filter_by(identifier=identifier).first():
            flash('Oś czasu o tym identyfikatorze już istnieje!', 'danger')
            return redirect(url_for('add_timeline'))
        
        new_timeline = Timeline(
            identifier=identifier,
            title=request.form.get('title'),
            description=request.form.get('description'),
            order=int(request.form.get('order', 0)),
            is_active='is_active' in request.form
        )
        
        db.session.add(new_timeline)
        db.session.commit()
        flash('Oś czasu dodana pomyślnie!', 'success')
        return redirect(url_for('manage_timelines'))
    
    return render_template('admin/add_timeline.html')

@app.route('/admin/timeline/<int:id>/add_event', methods=['GET', 'POST'])
def add_timeline_event(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    timeline = Timeline.query.get_or_404(id)
    
    if request.method == 'POST':
        new_event = TimelineEvent(
            timeline_id=id,
            title=request.form.get('title'),
            description=request.form.get('description'),
            date=request.form.get('date'),
            order=int(request.form.get('order', 0)))
        
        db.session.add(new_event)
        db.session.commit()
        flash('Wydarzenie dodane pomyślnie!', 'success')
        return redirect(url_for('edit_timeline', identifier=timeline.identifier))
    
    return render_template('admin/add_timeline_event.html', timeline=timeline)

@app.route('/admin/timeline/<int:id>/delete', methods=['POST'])
def delete_timeline(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    timeline = Timeline.query.get_or_404(id)
    
    # Najpierw usuń powiązane wydarzenia
    TimelineEvent.query.filter_by(timeline_id=id).delete()
    
    # Następnie usuń sam timeline
    db.session.delete(timeline)
    db.session.commit()
    
    flash('Oś czasu i jej wydarzenia zostały usunięte!', 'success')
    return redirect(url_for('manage_timelines'))

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

    # Znajdź lub stwórz gracza
    player = Player.query.filter_by(name=name, avatar=avatar).first()
    if not player:
        player = Player(name=name, avatar=avatar, score=0)
        db.session.add(player)

    # Zawsze aktualizuj czas startu przy rozpoczęciu gry
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
    timeline = Timeline.query.filter_by(identifier=identifier).first()
    return timeline.id if timeline else 1  # domyślnie pierwszy timeline

@app.route('/timeline')
def timeline():
    if "player_id" not in session:
        return redirect(url_for("logowanie"))
    
    # Pobierz ID osi czasu z URL (np. ?timeline_id=timeline-1)
    timeline_id = request.args.get('timeline_id')
    
    # Sprawdź czy gracz już ukończył tę oś
    if f"completed_{timeline_id}" in session:
        return redirect(url_for('next_step'))  # Jeśli tak, od razu przejdź dalej
    
    # Pobierz 3 wydarzenia z bazy
    events = TimelineEvent.query.filter_by(timeline_id=timeline_id).order_by(TimelineEvent.order).limit(3).all()
    
    # Zapisz w sesji, że oś została ukończona
    session[f"completed_{timeline_id}"] = True
    
    return render_template('timeline.html', 
                         events=events,
                         timeline_id=timeline_id)
    
   ## obsluga czasu cala


  

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
    next_step_identifier = get_next_step(player.current_step)
    
    player.current_step = next_step_identifier
    db.session.commit()
    
    return redirect(url_for(get_step_route(next_step_identifier)))

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


@app.route("/admin/data")
def show_data():
    if not session.get('admin_logged_in'):
        return jsonify({"error": "Brak dostępu"}), 403

    players = Player.query.all()
    questions = QuizQuestion.query.all()
    timelines = Timeline.query.all()

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
        ],
        "timelines": [
            {
                "id": t.id,
                "identifier": t.identifier,
                "title": t.title,
                "description": t.description,
                "events_count": len(t.events)
            } for t in timelines
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

if __name__ == "__main__":
    app.run(debug=True)





    