from flask import Flask
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')

db = SQLAlchemy()
migrate = Migrate()

def init_app(app: Flask):
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)

# flask db init  -> create migrate db instance
# flask db migrate -m "description" -> used to save the model changes to database
# flask db upgrade  -> to to upgrade db with new changes
# run this only when there are changes to db