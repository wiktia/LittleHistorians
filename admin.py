import os
from dotenv import load_dotenv
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash
from models import db, GameStep, QuizQuestion, Timeline, TimelineEvent, Player


load_dotenv(dotenv_path='config.env')

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin', methods=['GET', 'POST'])
def admin_login():
    admin_password_hash = os.getenv('ADMIN_PASSWORD_HASH')

    if request.method == 'POST':
        input_password = request.form.get('password')
        if check_password_hash(admin_password_hash, input_password):
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

@admin_bp.route('/admin/step/edit/<int:id>', methods=['GET', 'POST'])
def edit_step(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    step = GameStep.query.get_or_404(id)
    if request.method == 'POST':
        step.game_type = request.form['game_type']
        step.order = int(request.form['order'])
        step.is_active = 'is_active' in request.form
        db.session.commit()
        flash('Krok zaktualizowany!', 'success')
        return redirect(url_for('admin.manage_steps'))
    
    return render_template('admin/edit_step.html', step=step)

@admin_bp.route('/admin/step/add', methods=['GET', 'POST'])
def add_step():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    if request.method == 'POST':
        game_type = request.form['game_type']
        step_number = request.form['step_number']
        step_identifier = f"{game_type}-{step_number}"
        
        if GameStep.query.filter_by(step_identifier=step_identifier).first():
            flash('Krok o tym identyfikatorze już istnieje!', 'danger')
            return redirect(url_for('admin.add_step'))
        
        try:
            order = int(request.form['order'])
        except ValueError:
            flash('Pole "order" musi być liczbą całkowitą!', 'danger')
            return redirect(url_for('admin.add_step'))
        
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
        return redirect(url_for('admin.manage_steps'))
    
    return render_template('admin/add_step.html')

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
        return redirect(url_for('admin.manage_timelines'))
    
    return render_template('admin/edit_timeline.html', timeline=timeline)
    
@admin_bp.route('/admin/timeline/add', methods=['GET', 'POST'])
def add_timeline():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        if Timeline.query.filter_by(identifier=identifier).first():
            flash('Oś czasu o tym identyfikatorze już istnieje!', 'danger')
            return redirect(url_for('admin.add_timeline'))
        
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
        return redirect(url_for('admin.manage_timelines'))
    
    return render_template('admin/add_timeline.html')

@admin_bp.route('/admin/timeline/<int:id>/add_event', methods=['GET', 'POST'])
def add_timeline_event(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
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
        return redirect(url_for('admin.edit_timeline', identifier=timeline.identifier))
    
    return render_template('admin/add_timeline_event.html', timeline=timeline)

@admin_bp.route('/admin/timeline/<int:id>/delete', methods=['POST'])
def delete_timeline(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    timeline = Timeline.query.get_or_404(id)
    
    # Najpierw usuń powiązane wydarzenia
    TimelineEvent.query.filter_by(timeline_id=id).delete()
    
    # Następnie usuń sam timeline
    db.session.delete(timeline)
    db.session.commit()
    
    flash('Oś czasu i jej wydarzenia zostały usunięte!', 'success')
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