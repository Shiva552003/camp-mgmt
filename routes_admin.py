from flask import render_template,session
from wrappers import login_required, admin_required
from main import app


@app.route('/home')
@login_required
def admin_home():
    return render_template('home_admin.html', active='home',user=session['username'])

@app.route('/find')
def admin_find():
    return render_template('find.html', active='find')

@app.route('/stats')
def admin_stats():
    return render_template('stats.html', active='stats')