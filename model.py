from flask_sqlalchemy import SQLAlchemy
from main import app
from datetime import datetime
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
db.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10), nullable=False)

    influencer = db.relationship('Influencer', backref='user', uselist=False, cascade='all, delete-orphan')
    sponsor = db.relationship('Sponsor', backref='user', uselist=False, cascade='all, delete-orphan')

class Sponsor(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=True)
    company_name = db.Column(db.String(30))
    industry = db.Column(db.String(30), nullable=True)
    desc = db.Column(db.String(256), nullable=True)
    is_flagged = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    cover_photo = db.Column(db.LargeBinary, nullable=False)
    amt_spent = db.Column(db.Integer, default=0)

    campaigns = db.relationship('Campaign', backref='sponsor', lazy=True, cascade='all, delete-orphan')
    ads = db.relationship('Ad', backref='sponsor', lazy=True, cascade='all, delete-orphan')
    ad_requests = db.relationship('Ad_request', backref='sponsor', lazy=True, cascade='all, delete-orphan')

class Influencer(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    desc = db.Column(db.String(256))
    industry = db.Column(db.String(40))
    niche = db.Column(db.String(40))
    cover_photo = db.Column(db.LargeBinary, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_flagged = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float)

    insta_id = db.Column(db.String(40))
    insta_followers = db.Column(db.String(8))
    youtube_id = db.Column(db.String(40))
    youtube_channel = db.Column(db.String(40))
    youtube_followers = db.Column(db.String(8))
    x_id = db.Column(db.String(40))
    x_name = db.Column(db.String(40))
    x_followers = db.Column(db.String(8))

    ads = db.relationship('Ad', backref='influencer', lazy=True, cascade='all, delete-orphan')
    ad_requests = db.relationship('Ad_request', backref='influencer', lazy=True, cascade='all, delete-orphan')

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spon_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255))
    category = db.Column(db.String(50))
    status = db.Column(db.String(20))
    start_date = db.Column(db.Date, nullable=True)  
    end_date = db.Column(db.Date, nullable=True)  
    goal_users = db.Column(db.String(80))
    is_flagged = db.Column(db.Boolean)

    ads = db.relationship('Ad', backref='campaign', lazy=True, cascade='all, delete-orphan')

class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    influ_id = db.Column(db.Integer, db.ForeignKey('influencer.id'))
    spon_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'))
    ad_name = db.Column(db.String(80), nullable=False)
    ad_description = db.Column(db.String(255))
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    ad_status = db.Column(db.String(20))
    is_flagged = db.Column(db.Boolean)
    amount = db.Column(db.Integer)
    payment_status = db.Column(db.String(20))

class Ad_request(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    influ_id = db.Column(db.Integer, db.ForeignKey('influencer.id'))
    spon_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'))
    comments = db.Column(db.String(80), nullable=True)
    amount = db.Column(db.Integer)
    growth_promise = db.Column(db.String(10))
    previous_request_id = db.Column(db.Integer, db.ForeignKey('ad_request.id'), nullable=True)
    
    previous_request = db.relationship('Ad_request', remote_side=[id], backref='new_versions')

class is_verified(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    status = db.Column(db.String(10))

with app.app_context():
    db.create_all()
    admin = User.query.filter_by(role="admin").first()
    if not admin:
        obj = User(id="1", username="admin", password=generate_password_hash("admin123"), role="admin")
        db.session.add(obj)
        db.session.commit()

    #  db.relationship ('class name', backref='attribute not the class' , lazy: fetches data only when asked for, cascade = 'deleted a category ? delete its products as well')
    # the campaign id is the foreign key of , the "campaign.id" breakdown -> before '.' is the table name and after '.' is the primary key