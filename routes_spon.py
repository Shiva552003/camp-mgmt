from flask import render_template,session
from main import app
from model import Sponsor


@app.route('/home/sponsor')
def spon_home():
    spon=Sponsor.query.filter_by()
    return render_template('sponsor/home_spon.html', active='home', spon=session['username'])

@app.route('/find/sponsor')
def spon_find():
    return render_template('sponsor/find.html', active='find')

@app.route('/stats/sponsor')
def spon_stats():
    return render_template('sponsor/stats.html', active='stats')