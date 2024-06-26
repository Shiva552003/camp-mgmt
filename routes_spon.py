from flask import render_template,session,send_file,redirect,url_for
from main import app
from model import Sponsor
from wrappers import sponsor_required
import io


@app.route('/home/sponsor')
@sponsor_required
def spon_home():
    spon=Sponsor.query.filter_by(id=session['userId']).first();
    cover_photo= url_for('get_cover_photo', sponsor_id=spon.id)


    return render_template('sponsor/home_spon.html', active='home', spon=spon,cover_photo=cover_photo)

@app.route('/sponsor/<int:sponsor_id>/cover_photo')
def get_cover_photo(sponsor_id):
    sponsor = Sponsor.query.get_or_404(sponsor_id)
    if sponsor.cover_photo:
        return send_file(
            io.BytesIO(sponsor.cover_photo),
            mimetype='image/jpeg',
            as_attachment=False,
        )
    else:
        return redirect(url_for('home'))
    

@app.route('/campaign/sponsor')
@sponsor_required
def spon_campaigns():
    return render_template('sponsor/campaigns.html', active='campaigns')

@app.route('/find/sponsor')
@sponsor_required
def spon_find():
    return render_template('sponsor/find.html', active='find')

@app.route('/stats/sponsor')
@sponsor_required
def spon_stats():
    return render_template('sponsor/stats.html', active='stats')