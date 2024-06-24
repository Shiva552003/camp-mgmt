from flask_sqlalchemy import SQLAlchemy
from main import app
from datetime import datetime
from werkzeug.security import generate_password_hash
db= SQLAlchemy()
db.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username=db.Column(db.String(20), unique=True, nullable=False)
    password=db.Column(db.String(256), nullable=False)
    company_name=db.Column(db.String(45), nullable=True)
    role=db.Column(db.String(10),nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default = False)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(80), nullable=False,)
    budget = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255))
    category = db.Column(db.String(50))
    status = db.Column(db.String(20))
    start_date = db.Column(db.Date, nullable=False)  
    end_date = db.Column(db.Date, nullable=False)  
    goal = db.Column(db.String(80))

    ad=db.relationship('Ad',backref='campaign', lazy=True, cascade= 'all, delete-orphan')
    #  db.relationship ('class name', backref='attribute not the class' , lazy: fetches data only when asked for, cascade = 'deleted a category ? delete its products as well')

class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    ad_name = db.Column(db.String(80), nullable=False)
    ad_description = db.Column(db.String(255))
    ad_status = db.Column(db.String(20))
    payment_status = db.Column(db.String(20))
    target_type = db.Column(db.String(20))
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'),nullable=False)
    # the campaign id is the foreign key of , the "campaign.id" breakdown -> before '.' is the table name and after '.' is the promary key

with app.app_context():
    db.create_all()
    admin=User.query.filter_by(role="admin").first()
    if not admin:
      obj = User(id = "1",username = "admin",password = generate_password_hash("admin123"), company_name = "ADMIN",role="admin")
      db.session.add(obj)
      db.session.commit()

#! Irrelavant 
# class Cart(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
#     quantity = db.Column(db.Integer, nullable=False)

# class Transaction(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     datetime = db.Column(db.DateTime, nullable=False, default=datetime.now())
#     mode = db.Column(db.String(20), nullable=False)

# class Order(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False)
#     product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
#     quantity = db.Column(db.Integer, nullable=False)
#     price = db.Column(db.Float, nullable=False)
