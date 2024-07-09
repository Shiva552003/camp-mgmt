from flask import render_template,session, url_for,redirect,send_file
from main import app
from model import Influencer
import io


@app.route('/home/influencer')
def influ_home():
    influ=Influencer.query.filter_by(id=session['userId']).first()
    cover_photo= url_for('get_cover_photo_influ', influ_id=influ.id)

    return render_template('influencer/home_influ.html', active='home',influ=influ,cover_photo=cover_photo)

@app.route('/influ/<int:influ_id>/cover_photo')
def get_cover_photo_influ(influ_id):
    influencer = Influencer.query.get_or_404(influ_id)
    if influencer.cover_photo:
        return send_file(
            io.BytesIO(influencer.cover_photo),
            mimetype='image/jpeg',
            as_attachment=False,
        )
    else:
        return redirect(url_for('home'))

@app.route('/find/influencer')
def influ_find():
    return render_template('influencer/find.html', active='find')

@app.route('/campaigns/influencer')
def influ_camp():
    return render_template('influencer/campaign.html', active='find')

@app.route('/stats/influencer')
def influ_stats():
    return render_template('influencer/stats.html', active='stats')