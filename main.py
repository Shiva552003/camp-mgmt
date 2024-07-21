from flask import Flask
from config import init_app

app = Flask(__name__)
init_app(app)

import config
import model
import routes
import wrappers
import routes_admin
import routes_influ
import routes_spon