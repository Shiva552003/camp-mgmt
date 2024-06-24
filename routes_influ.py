from flask import render_template
from main import app


@app.route('/home/influencer')
def influ_home():
    return render_template('influencer/home_influ.html', active='home')

@app.route('/find/influencer')
def influ_find():
    return render_template('influencer/find.html', active='find')

@app.route('/stats/influencer')
def influ_stats():
    return render_template('influencer/stats.html', active='stats')