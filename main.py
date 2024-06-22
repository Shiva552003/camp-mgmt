from flask import Flask

app = Flask(__name__)

import config
import model
import routes
import wrappers
import routes_admin
import routes_influ
import routes_spon