from flask import render_template
from main import app


@app.route('/home/sponsor')
def spon_home():
    return render_template('home_spon.html', active='home')

@app.route('/find/sponsor')
def spon_find():
    return render_template('find.html', active='find')

@app.route('/stats/sponsor')
def spon_stats():
    return render_template('stats.html', active='stats')