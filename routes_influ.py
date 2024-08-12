from flask import flash, render_template, request,session, url_for,redirect,send_file
from main import app
from wrappers import influencer_required
from model import Influencer,Campaign, Ad_request,Ad, Sponsor
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
    pending_requests=Ad_request.query.filter(Ad_request.influ_id==influ.id, Ad_request.sender=='i',Ad_request.status!='R').all()

    return render_template('influencer/home_influ.html', active='home',influ=influ,cover_photo=cover_photo,live_campaigns=live_campaigns, new_requests=new_requests,pending_requests=pending_requests)

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

# @app.route('/find/influencer/<int:influ_id>')
# @influencer_required
# def influ_view(influ_id):
#     return render_template('influencer/find.html', active='find')


@app.route('/find/influ/Ads', methods=['GET', 'POST'])
@influencer_required
def influ_find_Ads():
    search_query = request.form.get('search_adName')
    status = request.form.get('status_html')

    if request.method == 'POST':
        return redirect(url_for('render_result_ads_influ',status=status,search_query=search_query))
    else:
        return render_template('influencer/find_ads_influ.html', active='find', findActive="ads", statusName=None)

@app.route('/find/influ/Ads/results', methods=['GET'])
@influencer_required
def render_result_ads_influ():
    search_query = request.args.get('search_query')
    status = request.args.get('status')
    current_date = date.today()
    ads = []
    adRs = []
    statusName=""

    if status and search_query:
        if status == 'All':
            ads = Ad.query.filter(Ad.influ_id == session['userId'],Ad.name.contains(search_query)).all()
            statusName="All Ads"
        elif status == 'live':
            ads = Ad.query.join(Campaign).filter(Ad.influ_id == session['userId'],Ad.name.contains(search_query),Campaign.end_date > current_date,Campaign.is_flagged.is_(False)).all()
            statusName="Live Ads"
        elif status == 'closed':
            ads = Ad.query.join(Campaign).filter(Ad.influ_id == session['userId'],Ad.name.contains(search_query),Campaign.end_date <= current_date).all()
            statusName="Expired Ads"
        elif status.startswith('ad_request_'):
            if status == 'ad_request_r':
                adRs = Ad_request.query.filter(Ad_request.influ_id == session['userId'],Ad_request.ad_name.contains(search_query),Ad_request.status=='rejected').all()
                statusName="Rejected Ad requests"
            elif status == 'ad_request_p':
                adRs = Ad_request.query.filter(Ad_request.influ_id == session['userId'],Ad_request.ad_name.contains(search_query),Ad_request.sender=='s',Ad_request.status!='rejected').all()
                statusName="Pending Ad requests"
            elif status == 'ad_request_n':
                adRs = Ad_request.query.filter(Ad_request.influ_id == session['userId'],Ad_request.ad_name.contains(search_query),Ad_request.sender=='i',Ad_request.status!='rejected').all()
                statusName="New Ad requests from Influencer"
    else:
        if status == 'All':
            ads = Ad.query.filter(Ad.influ_id == session['userId']).all()
            statusName="All Ads"
        elif status == 'live':
            ads = Ad.query.join(Campaign).filter(Ad.influ_id == session['userId'],Campaign.end_date > current_date,Campaign.is_flagged.is_(False)).all()
            statusName="Live Ads"
        elif status == 'closed':
            ads = Ad.query.join(Campaign).filter(Ad.influ_id == session['userId'],Campaign.end_date <= current_date).all()
            statusName="Expired Ads"
        elif status.startswith('ad_request_'):
            if status == 'ad_request_r':
                adRs = Ad_request.query.filter(Ad_request.influ_id == session['userId'],Ad_request.status=='R').all()
                statusName="Rejected Ad Requests"
            elif status == 'ad_request_p':
                adRs = Ad_request.query.filter(Ad_request.influ_id == session['userId'],Ad_request.sender=='s',Ad_request.status!='R').all()
                statusName="Pending Ad Requests"
            elif status == 'ad_request_n':
                adRs = Ad_request.query.filter(Ad_request.influ_id == session['userId'],Ad_request.sender=='i',Ad_request.status!='R').all()
                statusName="All New Ad requests from Influencer"

    if ads==[] and adRs==[]:
        flash("No Ads found", "danger")

    return render_template('influencer/find_ads_influ.html', active='find', findActive="ads", ads=ads, adRs=adRs, statusName=statusName)

@app.route('/find/influencer/Camp', methods=['GET', 'POST'])
@influencer_required
def influ_find_Camp():
    search_query= request.form.get('search_campName')
    spon_name= request.form.get('search_sponName')

    if request.method == 'POST':
        return redirect(url_for('render_result_camp_influ', spon_name=spon_name,search_query=search_query))
    else:
        return render_template('influencer/find_camp_influ.html', active='find', findActive="camp",statusName=None)

@app.route('/find/influencer/Camp/results', methods=['GET'])
@influencer_required
def render_result_camp_influ():
    search_query = request.args.get('search_query')
    spon_name = request.args.get('spon_name')
    current_date = date.today()
    camps = []

    if spon_name and search_query:
        camps = Campaign.query.join(Sponsor).filter(Sponsor.name.contains(spon_name),Campaign.name.contains(search_query),Campaign.status!="private").all()
    elif spon_name:
        camps = Campaign.query.join(Sponsor).filter(Sponsor.name.contains(spon_name), Campaign.status!="private").all()
    elif search_query:
        camps = Campaign.query.filter(Campaign.name.contains(search_query),Campaign.status!="private").all()
    if not camps:
        flash("No Campaign found", "danger")

    return render_template('influencer/find_camp_influ.html', active='find', findActive="camp", camps=camps)

@app.route('/find/influ', methods=['GET', 'POST'])
@influencer_required
def influ_find():
    query=request.form.get('search_Name')
    results=[]
    if(query):
        results = Sponsor.query.filter(Sponsor.name.contains(query),Sponsor.is_flagged.is_(False)).all()
    else:
        results = Sponsor.query.filter(Sponsor.is_flagged.is_(False)).all()
    if(request.method=='POST' and results==[]):
        flash('No Sponsor found','danger')
    if(request.method=='GET'):
        results=[]

    return render_template('influencer/find_spon.html', active='find', findActive="spon",sponsors=results)

@app.route('/find/all_camps', methods=['GET', 'POST'])
@influencer_required
def all_camps_of_spon():
    spon_id=request.args.get('spon_id')
    current_date = date.today()
    if(spon_id):
        results = Campaign.query.filter(Campaign.spon_id==spon_id,Campaign.is_flagged.is_(False),Campaign.end_date > current_date,Campaign.status!="private").all()

    return render_template('influencer/view_campaign.html', active='find',campaign=results)


@app.route('/stats/influencer')
@influencer_required
def influ_stats():
    return render_template('influencer/stats.html', active='stats')