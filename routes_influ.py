from flask import render_template,session, url_for,redirect,send_file
from main import app
from wrappers import influencer_required
from model import Influencer,Campaign, Ad_request,Ad
import io
from datetime import date

#! list of routes and thier functions


@app.route('/home/influencer')
@influencer_required
def influ_home():
    influ=Influencer.query.filter_by(id=session['userId']).first()
    cover_photo= url_for('get_cover_photo_influ', influ_id=influ.id)
    current_date = date.today()

    campaign_ids = Ad.query.with_entities(Ad.campaign_id).filter(Ad.influ_id == influ.id).distinct().all()
    campaign_ids = [id[0] for id in campaign_ids]  # used to convert list of tuples to list of ids

    live_campaigns = Campaign.query.filter(Campaign.id.in_(campaign_ids), Campaign.start_date < current_date, Campaign.end_date > current_date).all()

    new_requests=Ad_request.query.filter(Ad_request.influ_id==influ.id, Ad_request.sender=='s',Ad_request.status!='R').all()
    camp_history= Campaign.query.filter(Campaign.id.in_(campaign_ids),Campaign.end_date < current_date).all()

    return render_template('influencer/home_influ.html', active='home',influ=influ,cover_photo=cover_photo,live_campaigns=live_campaigns, new_requests=new_requests,camp_history=camp_history)

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

@app.route('/find/influencer/<int:influ_id>')
@influencer_required
def influ_view(influ_id):
    return render_template('influencer/find.html', active='find')


@app.route('/find/influencer')
@influencer_required
def influ_find():
    return render_template('influencer/find_influ.html', active='find')

@app.route('/campaigns/influencer')
@influencer_required
def influ_campaigns():
    return render_template('influencer/campaigns.html', active='campaigns')

@app.route('/stats/influencer')
@influencer_required
def influ_stats():
    return render_template('influencer/stats.html', active='stats')