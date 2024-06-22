from flask import render_template
from main import app


@app.route('/home/influencer')
def influ_home():
    return render_template('home_influ.html', active='home')

@app.route('/find/influencer')
def influ_find():
    return render_template('find.html', active='find')

@app.route('/stats/influencer')
def influ_stats():
    return render_template('stats.html', active='stats')