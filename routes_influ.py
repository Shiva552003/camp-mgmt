from operator import or_
from flask import flash, render_template, request,session, url_for,redirect,send_file
from main import app
from wrappers import influencer_required
from model import Influencer,Campaign, Ad_request,Ad, Sponsor,db
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
                adRs = Ad_request.query.filter(Ad_request.influ_id == session['userId'],Ad_request.ad_name.contains(search_query),Ad_request.sender=='i',Ad_request.status!='rejected').all()
                statusName="Pending Ad requests"
            elif status == 'ad_request_n':
                adRs = Ad_request.query.filter(Ad_request.influ_id == session['userId'],Ad_request.ad_name.contains(search_query),Ad_request.sender=='s',Ad_request.status!='rejected').all()
                statusName="New Ad requests from Sponsor"
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
                adRs = Ad_request.query.filter(Ad_request.influ_id == session['userId'],Ad_request.sender=='i',Ad_request.status!='R').all()
                statusName="Pending Ad Requests"
            elif status == 'ad_request_n':
                adRs = Ad_request.query.filter(Ad_request.influ_id == session['userId'],Ad_request.sender=='s',Ad_request.status!='R').all()
                statusName="All New Ad requests from Sponsor"

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
        camps = Campaign.query.join(Sponsor).filter(Sponsor.name.contains(spon_name)).all()
        print(camps)
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
        results = Campaign.query.filter(Campaign.spon_id==spon_id,Campaign.is_flagged.is_(False),Campaign.end_date > current_date,or_(Campaign.status != "private", Campaign.status.is_(None))).all()

    return render_template('influencer/view_all_campaigns.html', active='find',campaign=results)


@app.route('/send/influ/ad_req', methods=['GET', 'POST'])
@influencer_required
def send_ad_request_influ():
    camp_id = request.args.get('camp_id')
    current_date = date.today()
    print("camp id", camp_id)
    campaign = Campaign.query.get(camp_id)
    
    if request.method == 'POST':
        ad_name = request.form.get('ad_name')
        budget = request.form.get('budget')
        comments = request.form.get('comments')
        growth_promise = request.form.get('growth_promise')
        influ_id = session['userId']
        spon_id = campaign.spon_id
        
        new_ad_request = Ad_request(
            ad_name=ad_name,
            influ_id=influ_id,
            spon_id=spon_id,
            comments=comments,
            amount=budget,
            campaign_id=camp_id,
            growth_promise=growth_promise,
            sender='i',
            status="P"
        )
        
        db.session.add(new_ad_request)
        db.session.commit()
        flash("Successful","success")
        return redirect(url_for('influ_home'))

    return render_template('influencer/influ_ad_request.html',active='find',campaign=campaign)


@app.route('/edit/influencer/<int:influ_id>', methods=['GET', 'POST'])
def edit_view_influencer(influ_id):
    influencer = Influencer.query.get(influ_id)
    edit = request.args.get('edit', False)
    
    if request.method == 'POST':
        influencer.name = request.form['name']
        influencer.desc = request.form['desc']
        influencer.industry = request.form['industry']
        influencer.niche = request.form['niche']
        influencer.insta_id = request.form['insta_id']
        influencer.insta_followers = request.form['insta_followers']
        influencer.youtube_id = request.form['youtube_id']
        influencer.youtube_channel = request.form['youtube_channel']
        influencer.youtube_followers = request.form['youtube_followers']
        influencer.x_id = request.form['x_id']
        influencer.x_name = request.form['x_name']
        influencer.x_followers = request.form['x_followers']
        
        db.session.commit()
        flash("Successful","success")
        return redirect(url_for('influ_home'))
    
    return render_template('influencer/view_details.html',influencer=influencer,edit=edit)

@app.route('/influencer/view/ad_request')
def view_ad_request_influ():
    req_id = request.args.get('req_id')
    only_view = request.args.get('only_view',False)
    ad_request=Ad_request.query.get(req_id);
    sponsor = Sponsor.query.get(ad_request.spon_id)
    influencer = Influencer.query.get(ad_request.influ_id)
    camp=Campaign.query.get(ad_request.campaign_id)

    return render_template('influencer/view_ad_request.html',active="home",ad_request=ad_request,sponsor=sponsor,influencer=influencer,camp=camp,only_view=only_view)

@app.route('/influ/accept/ad_req')
def accept_ad_request_influ():
    req_id = request.args.get('req_id')
    ad_request = Ad_request.query.get(req_id)
    
    if ad_request:
        new_ad = Ad(influ_id=ad_request.influ_id,spon_id=ad_request.spon_id,campaign_id=ad_request.campaign_id,name=ad_request.ad_name,desc=ad_request.comments,ad_status='Pending',is_flagged=False,amount=ad_request.amount,payment_status='Not Paid')

        db.session.add(new_ad)
        db.session.delete(ad_request)
        db.session.commit()
        flash("Successful","success")
    return redirect(url_for('influ_home'))

@app.route('/influ/reject/ad_req')
def reject_ad_request_influ():
    req_id = request.args.get('req_id')
    ad_request = Ad_request.query.get(req_id)
    
    ad_request.status='R'
    db.session.commit()
    flash('Operation successful', 'success')
    return redirect(url_for('influ_home'))

@app.route('/stats/influencer')
@influencer_required
def influ_stats():
    return render_template('influencer/stats.html', active='stats')

@app.route('/influ/view_campaign/<int:camp_id>')
def influ_view_camp(camp_id):
    camp = Campaign.query.filter_by(id=camp_id).first()
    ads = Ad.query.filter_by(campaign_id=camp.id).all()
    current_date = date.today()


    return render_template('influencer/view_camp.html', active='home', camp=camp,ads=ads)
