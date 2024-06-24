from flask import render_template,session
from wrappers import admin_required
from model import User
from main import app


@app.route('/home')
@admin_required
def admin_home():
    return render_template('admin/home_admin.html', active='home',user=session['username'])

@app.route('/find')
@admin_required
def admin_find():
    sponsors=User.query.filter_by(role="sponsor").all()
    influencers=User.query.filter_by(role="influencer").all()

    return render_template('admin/find_admin.html', active='find',sponsors=sponsors,influencers=influencers)

@app.route('/stats')
@admin_required
def admin_stats():
    return render_template('stats.html', active='stats')