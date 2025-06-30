from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, GameStep, QuizQuestion, Timeline, TimelineEvent
from models import Player
admin_bp = Blueprint('admin', __name__)

# Panel administracyjny
@admin_bp.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == 'maslo': # TODO: zmienić na bezpieczne hasło
            session['admin_logged_in'] = True
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Nieprawidłowe hasło', 'danger')
    return render_template('admin/login.html')

@admin_bp.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    questions = QuizQuestion.query.all()
    timelines = Timeline.query.count()
    return render_template('admin/dashboard.html', questions=questions, timelines=timelines)

@admin_bp.route('/admin/steps')
def manage_steps():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    steps = GameStep.query.order_by(GameStep.order).all()
    return render_template('admin/steps.html', steps=steps)

# Dodaj nowy krok
@admin_bp.route('/admin/steps/add', methods=['GET', 'POST'])
def add_step():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    if request.method == 'POST':
        try:
            # Walidacja identyfikatora
            step_identifier = request.form['step_identifier']
            if GameStep.query.filter_by(step_identifier=step_identifier).first():
                flash('Krok o tym identyfikatorze już istnieje!', 'danger')
                return redirect(url_for('admin.add_step'))
            
            # Konwersja kolejności na int z obsługą błędów
            order = int(request.form['order'])
            
            new_step = GameStep(
                step_identifier=step_identifier,
                game_type=request.form['game_type'],
                order=order,
                is_active='is_active' in request.form
            )
            
            db.session.add(new_step)
            db.session.commit()
            flash('Krok gry dodany pomyślnie!', 'success')
            return redirect(url_for('admin.manage_steps'))
        
        except ValueError:
            flash('Nieprawidłowa wartość dla pola "Kolejność" - musi być liczbą całkowitą', 'danger')
        except KeyError as e:
            flash(f'Brak wymaganego pola: {e}', 'danger')
        except Exception as e:
            flash(f'Błąd podczas dodawania kroku: {str(e)}', 'danger')
    
    return render_template('admin/add_step.html')

# Edytuj krok (musisz dodać podobne zmiany jak w add_step)
@admin_bp.route('/admin/steps/<int:id>/edit', methods=['GET', 'POST'])
def edit_step(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    step = GameStep.query.get_or_404(id)
    
    if request.method == 'POST':
        step.step_identifier = request.form['step_identifier']
        step.game_type = request.form['game_type']
        step.order = int(request.form['order'])
        step.is_active = 'is_active' in request.form
        
        db.session.commit()
        flash('Krok gry zaktualizowany!', 'success')
        return redirect(url_for('admin.manage_steps'))
    
    return render_template('admin/edit_step.html', step=step)

@admin_bp.route('/admin/step/delete/<int:id>', methods=['POST'])
def delete_step(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    step = GameStep.query.get_or_404(id)
    
    # Zabezpieczenie przed usunięciem stałych kroków
    if step.step_identifier in ['start', 'login', 'end']:
        flash('Nie można usunąć stałego kroku gry!', 'danger')
        return redirect(url_for('admin.manage_steps'))
    
    db.session.delete(step)
    db.session.commit()
    flash('Krok usunięty pomyślnie!', 'success')
    return redirect(url_for('admin.manage_steps'))

@admin_bp.route('/admin/question/add', methods=['GET', 'POST'])
def add_question():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
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
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('admin/add_question.html')

@admin_bp.route('/admin/question/edit/<int:id>', methods=['GET', 'POST'])
def edit_question(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
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
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('admin/edit_question.html', question=question)

@admin_bp.route('/admin/question/delete/<int:id>', methods=['POST'])
def delete_question(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    question = QuizQuestion.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    flash('Pytanie usunięte pomyślnie!', 'success')
    return redirect(url_for('admin.admin_dashboard'))

# Timeline management
@admin_bp.route('/admin/timelines')
def manage_timelines():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    timelines = Timeline.query.order_by(Timeline.order).all()
    return render_template('admin/timelines.html', timelines=timelines)

@admin_bp.route('/admin/timeline/<string:identifier>', methods=['GET', 'POST'])
def edit_timeline(identifier):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    timeline = Timeline.query.filter_by(identifier=identifier).first_or_404()
    
    if request.method == 'POST':
        # Uproszczona aktualizacja - tylko podstawowe dane
        timeline.title = request.form['title']
        timeline.is_active = 'is_active' in request.form
        db.session.commit()
        
        flash('Oś czasu zaktualizowana!', 'success')
        return redirect(url_for('admin.manage_timelines'))
    
    return render_template('admin/edit_timeline.html', timeline=timeline)

@admin_bp.route('/admin/timeline/add', methods=['GET', 'POST'])
def add_timeline():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    if request.method == 'POST':
        identifier = request.form['identifier']
        
        # Sprawdź unikalność identyfikatora
        if Timeline.query.filter_by(identifier=identifier).first():
            flash('Oś czasu o tym identyfikatorze już istnieje!', 'danger')
            return redirect(url_for('admin.add_timeline'))
        
        new_timeline = Timeline(
            identifier=identifier,
            title=request.form['title'],
            is_active='is_active' in request.form
        )
        
        db.session.add(new_timeline)
        db.session.commit()
        flash('Oś czasu dodana pomyślnie!', 'success')
        return redirect(url_for('admin.manage_timelines'))
    
    return render_template('admin/add_timeline.html')

@admin_bp.route('/admin/timeline/<string:identifier>/add_event', methods=['GET', 'POST'])
def add_timeline_event(identifier):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    timeline = Timeline.query.filter_by(identifier=identifier).first_or_404()
    
    if request.method == 'POST':
        new_event = TimelineEvent(
            timeline_id=timeline.id,
            title=request.form['title'],
            year=int(request.form['year']),  # Proste pole roku
            order=0  # Domyślna kolejność
        )
        
        db.session.add(new_event)
        db.session.commit()
        flash('Wydarzenie dodane pomyślnie!', 'success')
        return redirect(url_for('admin.edit_timeline', identifier=identifier))
    
    return render_template('admin/add_timeline_event.html', timeline=timeline)

@admin_bp.route('/admin/timeline/<string:identifier>/delete', methods=['POST'])
def delete_timeline(identifier):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    timeline = Timeline.query.filter_by(identifier=identifier).first_or_404()
    db.session.delete(timeline)
    db.session.commit()
    
    flash('Oś czasu została usunięta!', 'success')
    return redirect(url_for('admin.manage_timelines'))

@admin_bp.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.admin_login'))


#Dane admina
@admin_bp.route("/admin/data")
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

@admin_bp.route('/admin/clear_players', methods=['POST'])
def clear_players():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    Player.query.delete()
    db.session.commit()
    flash('Wszyscy gracze zostali usunięci.', 'warning')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/ranking')
def admin_ranking():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    players = Player.query.order_by(Player.score.desc()).all()
    return render_template('admin/ranking.html', players=players)