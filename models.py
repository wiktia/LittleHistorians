from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Modele
class GameStep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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
    year = db.Column(db.Integer)
    order = db.Column(db.Integer)  

    timeline = db.relationship('Timeline', backref='events')