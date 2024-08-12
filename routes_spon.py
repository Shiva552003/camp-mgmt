from flask import render_template,session,send_file,redirect,url_for,request,flash
from sqlalchemy import desc,func
from main import app
from model import Ad_request, Sponsor,Campaign,db,Ad,Influencer
from wrappers import sponsor_required
from datetime import datetime,date
import io

#! list of routes and its purpose
# 1. spon_home -> load the home page for spon, loads, live campaigns, requests, and pending requests
# 2. get_cover_photo -> loads the cover photo from blob into image
# 3. spon_campaigns -> loads the campaign and campaigns page, loads live, closed 
# 4. add_campaigns -> add campaign page, just plain function call
# 5. add_campaigns_post -> to handle the add campaign post request
# 6. 
# 7.
# 8.
# 9.
# 10.
# 11. spon_find_ads 
# 12. spon_find_campaign
# 13. spon_find_influencers
# 14. spon_stats -> shows stats page for sponsors
# 15. view_spon_details -> to view all the details


@app.route('/home/sponsor')
@sponsor_required
def spon_home():
    spon=Sponsor.query.filter_by(id=session['userId']).first()
    cover_photo= url_for('get_cover_photo', sponsor_id=spon.id)
    current_date = date.today()

    campaigns=Campaign.query.filter(Campaign.spon_id==spon.id,Campaign.start_date < current_date, Campaign.end_date > current_date).all()
    requests = db.session.query(Ad_request, Influencer.name.label('influ_name')).\
    join(Influencer, Ad_request.influ_id == Influencer.id).\
    filter(Ad_request.spon_id == spon.id, Ad_request.sender == "i",Ad_request.status!="R").all()

    pen_requests = db.session.query(Ad_request, Influencer.name.label('influ_name')).\
    join(Influencer, Ad_request.influ_id == Influencer.id).\
    filter(Ad_request.spon_id == spon.id, Ad_request.sender == "s", Ad_request.status!="R").all()

    return render_template('sponsor/home_spon.html', active='home', spon=spon,cover_photo=cover_photo,campaigns=campaigns,requests=requests,pen_requests=pen_requests)

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
    current_date = date.today()
    
    spon=Sponsor.query.filter_by(id=session['userId']).first()
    live_camp=Campaign.query.filter(Campaign.spon_id==spon.id,Campaign.start_date < current_date, Campaign.end_date > current_date).all()
    closed_camp=Campaign.query.filter(Campaign.spon_id==spon.id, Campaign.end_date < current_date, Campaign.is_flagged.is_(False)).all()
    flagged_camp=Campaign.query.filter(Campaign.spon_id==spon.id, Campaign.is_flagged == True).all()

    no_of_ads = Ad.query.filter_by(spon_id=spon.id).count()
    no_of_collabs = Ad.query.filter_by(spon_id=spon.id).distinct(Ad.influ_id).count()
    no_of_camps = Campaign.query.filter_by(spon_id=spon.id).count()
    total_amount_spent = Ad.query.with_entities(func.sum(Ad.amount)).filter_by(spon_id=spon.id).scalar()

    return render_template('sponsor/campaigns.html', active='campaigns',live_campaigns=live_camp, closed_campaigns=closed_camp, flagged_camp=flagged_camp
                        , no_of_ads=no_of_ads, no_of_collabs=no_of_collabs, total_amount_spent=total_amount_spent,no_of_camps=no_of_camps)

@app.route('/sponsor/add_campaign')
@sponsor_required
def add_campaigns():
    camp={}
    return render_template('sponsor/add_campaign.html', active='campaigns',camp=camp)

@app.route('/sponsor/add_campaign', methods=['POST'])
@sponsor_required
def add_campaigns_Post():
    name = request.form.get('name_html')
    budget = request.form.get('budget_html')
    desc = request.form.get('desc_html')
    industry = request.form.get('industry_html')
    s_date = request.form.get('start_date_html')
    e_date = request.form.get('end_date_html')
    goal = request.form.get('goal_users_html')
    visibility = request.form.get('visibility')

    camp={'name':name, 'budget':budget,'desc':desc,'industry': industry,'start_date':s_date,'end_date':e_date,'status':visibility}

    s_date = datetime.strptime(s_date, '%Y-%m-%d').date() if s_date else None
    e_date = datetime.strptime(e_date, '%Y-%m-%d').date() if e_date else None
    
    if not name or not budget or not industry or not s_date:
        flash('Please enter all the required fields','danger')
        return render_template('sponsor/add_campaign.html', active='campaigns',camp=camp)
    else:
        campaign = Campaign(
            spon_id=session['userId'],
            name=name,
            budget=budget,
            desc=desc,
            category=industry,
            start_date=s_date,
            end_date=e_date,
            goal_users=goal,
            is_flagged=False,
        )
        db.session.add(campaign)
        db.session.commit()
        return redirect(url_for('spon_view_camp',camp_id=campaign.id))

@app.route('/sponsor/view_campaign/<int:camp_id>')
@sponsor_required
def spon_view_camp(camp_id):
    camp = Campaign.query.filter_by(id=camp_id).first()
    ads = Ad.query.filter_by(campaign_id=camp.id).all()
    current_date = date.today()

    editable = False if camp.is_flagged or camp.end_date < current_date else True;

    return render_template('sponsor/view_camp.html', active='campaigns', camp=camp,ads=ads,editable=editable)

@app.route('/sponsor/update/spon', methods=['GET', 'POST'])
def update_camp():
    camp_id = request.args.get('camp_id')
    camp = Campaign.query.get(camp_id)

    if request.method == 'POST':
        camp.name = request.form.get('campaign_name')
        camp.budget = request.form.get('campaign_budget')
        camp.desc = request.form.get('campaign_description')
        camp.category = request.form.get('campaign_category')
        camp.start_date = datetime.strptime(request.form.get('campaign_start_date'), '%Y-%m-%d').date()
        camp.end_date = datetime.strptime(request.form.get('campaign_end_date'), '%Y-%m-%d').date()
        camp.goal_users = request.form.get('campaign_goal_users')
        db.session.commit()
        flash("Successfull","success")
        return redirect(url_for('spon_view_camp',camp_id=camp.id))
    
    return render_template('sponsor/update_camp.html', camp=camp)


@app.route('/sponsor/view_ad/<int:ad_id>')
def spon_view_ad(ad_id):
    ad = Ad.query.filter_by(id=ad_id).first()
    sponsor = Sponsor.query.get(ad.spon_id)
    influencer = Influencer.query.get(ad.influ_id)
    camp=Campaign.query.get(ad.campaign_id)

    return render_template('sponsor/view_ad.html', active='campaigns', ads=ad,sponsor=sponsor,camp=camp,influencer=influencer)


@app.route('/sponsor/update_ad/<int:ad_id>', methods=['GET', 'POST'])
def spon_update_ad(ad_id):
    ad = Ad.query.filter_by(id=ad_id).first()
    sponsor = Sponsor.query.get(ad.spon_id)
    influencer = Influencer.query.get(ad.influ_id)
    camp = Campaign.query.get(ad.campaign_id)

    if request.method == 'POST':
        ad.name = request.form.get('ad_name')
        ad.desc = request.form.get('comments')
        ad.amount = request.form.get('amount')
        db.session.commit()
        flash('Successful',"success")
        return redirect(url_for('spon_view_ad', ad_id=ad_id))

    return render_template('sponsor/view_ad.html',active='campaigns',ads=ad,sponsor=sponsor,camp=camp,influencer=influencer,edit=True)
@app.route('/sponsor/delete')
def delete_ad():
    ad_id=request.args.get('ad_id');
    ad = Ad.query.filter_by(id=ad_id).first()

    db.session.delete(ad)
    db.session.commit()
    return redirect(url_for('render_result_ads',status='live',search_query=''))


@app.route('/sponsor/add_ad')
def spon_add_ad():
    ad={}
    camp_id=request.args.get('camp_id')
    return render_template('sponsor/add_ad.html', active='campaigns',ad=ad, showInfluencers=False,camp_id=camp_id)

@app.route('/sponsor/add_ad', methods=['POST'])
def spon_search_in_add_ad():
    name = request.form.get('name_html')
    budget = request.form.get('budget_html')
    platform = request.form.get('platform_html')
    influ_name = request.form.get('search_influencerName')
    showInfluencers = request.form.get('showInfluencers')
    comments=request.form.get('comments_html')

    ad={"name":name,"budget":budget,"platform":platform,"influencerName":influ_name,"comments":comments}
    if platform == 'All':
        influencers = Influencer.query.filter(
            Influencer.name.like(f"%{influ_name}%"),
            Influencer.is_flagged == False
        ).all()
    elif platform == 'instagram':
        influencers = Influencer.query.filter(
            Influencer.name.like(f"%{influ_name}%"),
            Influencer.is_flagged == False,
            Influencer.insta_followers > 0
        ).order_by(desc(Influencer.insta_followers)).all()
    elif platform == 'youtube':
        influencers = Influencer.query.filter(
            Influencer.name.like(f"%{influ_name}%"),
            Influencer.is_flagged == False,
            Influencer.youtube_followers > 0
        ).order_by(desc(Influencer.youtube_followers)).all()
    elif platform == 'x':
        influencers = Influencer.query.filter(
            Influencer.name.like(f"%{influ_name}%"),
            Influencer.is_flagged == False,
            Influencer.x_followers > 0
        ).order_by(desc(Influencer.x_followers)).all()
    else:
        influencers=[]
        flash("Please provide plateform", "danger")

    return render_template('sponsor/add_ad.html', active='campaigns',ad=ad,influencers=influencers,showInfluencers=True)

@app.route('/sponsor/send_request/<int:influencer_id>',methods=['POST'])
def send_ad_request(influencer_id):
    name = request.form.get('name_html')
    budget = request.form.get('budget_html')
    comments = request.form.get('comments_html')
    camp_id=request.args.get('camp_id')

    if(name == "" or budget == "" or name == None or budget == None):
        flash("Please fill in all the fields","danger")
        return redirect(url_for('spon_add_ad'))
    
    ad_req = Ad_request(
        ad_name=name,
        influ_id=influencer_id,
        spon_id=session['userId'],
        amount=budget,
        comments=comments,
        sender="s",
        campaign_id=camp_id,
        previous_request_id=None,
        next_request_id=None,
        status="P"
    )

    db.session.add(ad_req)
    db.session.commit()
    return redirect(url_for('spon_home'))

@app.route('/sponsor/send_request/from_find',methods=['get'])
def send_ad_request_from_find():

    flash('Choose campaigns first','warning')
    return redirect(url_for('spon_campaigns'))



@app.route('/find/sponsor/Ads', methods=['GET', 'POST'])
@sponsor_required
def spon_find_Ads():
    search_query = request.form.get('search_adName')
    status = request.form.get('status_html')

    if request.method == 'POST':
        return redirect(url_for('render_result_ads',status=status,search_query=search_query))
    else:
        return render_template('sponsor/find_ads.html', active='find', findActive="ads", statusName=None)

@app.route('/find/sponsor/Ads/results', methods=['GET'])
@sponsor_required
def render_result_ads():
    search_query = request.args.get('search_query')
    status = request.args.get('status')
    current_date = date.today()
    ads = []
    adRs = []
    statusName=""

    if status and search_query:
        if status == 'All':
            ads = Ad.query.filter(Ad.spon_id == session['userId'],Ad.name.contains(search_query)).all()
            statusName="All Ads"
        elif status == 'live':
            ads = Ad.query.join(Campaign).filter(Ad.spon_id == session['userId'],Ad.name.contains(search_query),Campaign.end_date > current_date,Campaign.is_flagged.is_(False)).all()
            statusName="Live Ads"
        elif status == 'closed':
            ads = Ad.query.join(Campaign).filter(Ad.spon_id == session['userId'],Ad.name.contains(search_query),Campaign.end_date <= current_date).all()
            statusName="Expired Ads"
        elif status.startswith('ad_request_'):
            if status == 'ad_request_r':
                adRs = Ad_request.query.filter(Ad_request.spon_id == session['userId'],Ad_request.ad_name.contains(search_query),Ad_request.status=='rejected').all()
                statusName="Rejected Ad requests"
            elif status == 'ad_request_p':
                adRs = Ad_request.query.filter(Ad_request.spon_id == session['userId'],Ad_request.ad_name.contains(search_query),Ad_request.sender=='s',Ad_request.status!='rejected').all()
                statusName="Pending Ad requests"
            elif status == 'ad_request_n':
                adRs = Ad_request.query.filter(Ad_request.spon_id == session['userId'],Ad_request.ad_name.contains(search_query),Ad_request.sender=='i',Ad_request.status!='rejected').all()
                statusName="New Ad requests from Influencer"
    else:
        if status == 'All':
            ads = Ad.query.filter(Ad.spon_id == session['userId']).all()
            statusName="All Ads"
        elif status == 'live':
            ads = Ad.query.join(Campaign).filter(Ad.spon_id == session['userId'],Campaign.end_date > current_date,Campaign.is_flagged.is_(False)).all()
            statusName="Live Ads"
        elif status == 'closed':
            ads = Ad.query.join(Campaign).filter(Ad.spon_id == session['userId'],Campaign.end_date <= current_date).all()
            statusName="Expired Ads"
        elif status.startswith('ad_request_'):
            if status == 'ad_request_r':
                adRs = Ad_request.query.filter(Ad_request.spon_id == session['userId'],Ad_request.status=='R').all()
                statusName="Rejected Ad Requests"
            elif status == 'ad_request_p':
                adRs = Ad_request.query.filter(Ad_request.spon_id == session['userId'],Ad_request.sender=='s',Ad_request.status!='R').all()
                statusName="Pending Ad Requests"
            elif status == 'ad_request_n':
                adRs = Ad_request.query.filter(Ad_request.spon_id == session['userId'],Ad_request.sender=='i',Ad_request.status!='R').all()
                statusName="All New Ad requests from Influencer"

    if ads==[] and adRs==[]:
        flash("No Ads found", "danger")

    return render_template('sponsor/find_ads.html', active='find', findActive="ads", ads=ads, adRs=adRs, statusName=statusName)

@app.route('/find/sponsor/Camp', methods=['GET', 'POST'])
@sponsor_required
def spon_find_Camp():
    search_query= request.form.get('search_campName')
    status= request.form.get('status_html')

    if request.method == 'POST':
        return redirect(url_for('render_result_camp', status=status,search_query=search_query))
    else:
        return render_template('sponsor/find_camp.html', active='find', findActive="camp",statusName=None)

@app.route('/find/sponsor/Camp/results', methods=['GET'])
@sponsor_required
def render_result_camp():
    search_query = request.args.get('search_query')
    status = request.args.get('status')
    current_date = date.today()
    camps = []
    statusName = ""

    if status and search_query:
        if status == 'All':
            camps = Campaign.query.filter(Campaign.spon_id==session['userId'], Campaign.name.contains(search_query)).all()
            statusName = "All Campaigns"
        elif status == 'live':
            camps = Campaign.query.filter(Campaign.spon_id==session['userId'], Campaign.name.contains(search_query), Campaign.end_date > current_date, Campaign.is_flagged.is_(False)).all()
            statusName = "Live Campaigns"
        elif status == 'closed':
            camps = Campaign.query.filter(Campaign.spon_id==session['userId'], Campaign.name.contains(search_query), Campaign.end_date < current_date, Campaign.is_flagged.is_(False)).all()
            statusName = "Closed Campaigns"
        elif status == 'flagged':
            camps = Campaign.query.filter(Campaign.spon_id==session['userId'], Campaign.name.contains(search_query), Campaign.is_flagged).all()
            statusName = "Flagged Campaigns"
    else:
        if status == 'All':
            camps = Campaign.query.filter(Campaign.spon_id==session['userId']).all()
            statusName = "All Campaigns"
        elif status == 'live':
            camps = Campaign.query.filter(Campaign.spon_id==session['userId'], Campaign.end_date > current_date, Campaign.is_flagged.is_(False)).all()
            statusName = "Live Campaigns"
        elif status == 'closed':
            camps = Campaign.query.filter(Campaign.spon_id==session['userId'], Campaign.end_date < current_date, Campaign.is_flagged.is_(False)).all()
            statusName = "Closed Campaigns"
        elif status == 'flagged':
            camps = Campaign.query.filter(Campaign.spon_id==session['userId'], Campaign.is_flagged).all()
            statusName = "Flagged Campaigns"

    if camps == []:
        flash("No Campaign found","danger")

    return render_template('sponsor/find_camp.html', active='find', findActive="camp", camps=camps, statusName=statusName)

@app.route('/find/sponsor', methods=['GET', 'POST'])
@sponsor_required
def spon_find():
    query=request.form.get('search_influencerName')
    results=[]
    if(query):
        results = Influencer.query.filter(Influencer.name.contains(query),Influencer.is_flagged.is_(False)).all()
    else:
        results = Influencer.query.filter(Influencer.is_flagged.is_(False)).all()
    if(request.method=='POST' and results==[]):
        flash('No influencer found','danger')
    if(request.method=='GET'):
        results=[]

    return render_template('sponsor/find_influ.html', active='find', findActive="influ",influencers=results)

@app.route('/stats/sponsor')
@sponsor_required
def spon_stats():
    spon_id = session['userId']
    influencer_ids = db.session.query(Ad.influ_id).filter_by(spon_id=spon_id).distinct().all()
    influencer_ids = [id for (id,) in influencer_ids]

    total_amount_spent = db.session.query(func.sum(Ad.amount)).filter_by(spon_id=spon_id).scalar() or 0
    total_users_reached = db.session.query(func.sum(Influencer.insta_followers + Influencer.youtube_followers)).filter(Influencer.id.in_(influencer_ids)).scalar() or 0
    
    labels = ['Amount Spent', 'Users Reached']
    data = [total_amount_spent, total_users_reached]

    return render_template('sponsor/stats.html', active='stats', labels=labels, data=data)

@app.route('/view_spon_details')
@sponsor_required
def view_spon_details():
    spon=Sponsor.query.filter_by(id=session['userId']).first()
    cover_photo= url_for('get_cover_photo', sponsor_id=spon.id)

    return render_template('sponsor/view_spon_details.html', active='home', spon=spon,cover_photo=cover_photo,edit=False)


@app.route('/toggle_edit')
@sponsor_required
def toggle_edit():
    edit_mode = request.form.get('edit', 'false') == 'true'
    edit_mode = not edit_mode

    spon = Sponsor.query.filter_by(id=session['userId']).first()
    cover_photo = url_for('get_cover_photo', sponsor_id=spon.id)
    return render_template('sponsor/view_spon_details.html', active='home', spon=spon, cover_photo=cover_photo, edit=edit_mode)


@app.route('/save_sponsor_details', methods=['POST'])
@sponsor_required
def save_sponsor_details():
    spon = Sponsor.query.filter_by(id=session['userId']).first()

    spon.name = request.form.get('name')
    spon.company_name = request.form.get('company_name')
    spon.industry = request.form.get('industry')
    spon.desc = request.form.get('desc')
    spon.amt_spent = request.form.get('amt_spent')

    db.session.commit()
    return redirect(url_for('view_spon_details'))

@app.route('/view_all_live_camp')
def view_all_live_camp():
    return redirect(url_for('render_result_camp',status='live',search_query=None))

@app.route('/view_all_new_req')
def view_all_new_req():
    return redirect(url_for('render_result_ads',status='ad_request_n',search_query=None))
@app.route('/view_all_pending_req')
def view_all_pending_req():
    return redirect(url_for('render_result_ads',status='ad_request_p',search_query=None))

@app.route('/view/ad_request')
def view_ad_request():
    req_id = request.args.get('req_id')
    negotiate = request.args.get('negotiate')
    only_view = False
    only_view = request.args.get('only_view')
    ad_request=Ad_request.query.get(req_id);
    sponsor = Sponsor.query.get(ad_request.spon_id)
    influencer = Influencer.query.get(ad_request.influ_id)
    camp=Campaign.query.get(ad_request.campaign_id)

    return render_template('sponsor/view_ad_request.html',active="home",ad_request=ad_request,edit=False,sponsor=sponsor,influencer=influencer,camp=camp,only_view=only_view)

@app.route('/accept/ad_req')
def accept_ad_request():
    req_id = request.args.get('req_id')
    ad_request = Ad_request.query.get(req_id)
    
    if ad_request:
        new_ad = Ad(influ_id=ad_request.influ_id,spon_id=ad_request.spon_id,campaign_id=ad_request.campaign_id,name=ad_request.ad_name,desc=ad_request.comments,ad_status='Pending',is_flagged=False,amount=ad_request.amount,payment_status='Not Paid')

        db.session.add(new_ad)
        db.session.delete(ad_request)
        db.session.commit()
    return redirect(url_for('spon_home'))

@app.route('/reject/ad_req')
def reject_ad_request():
    req_id = request.args.get('req_id')
    ad_request = Ad_request.query.get(req_id)
    
    ad_request.status='R'
    flash('Operation successful', 'success')
    db.session.commit()
    return redirect(url_for('spon_home'))

@app.route('/delete/campaign')
def delete_campaign():
    camp_id=request.args.get('camp_id')

    camp=Campaign.query.get(camp_id)
    db.session.delete(camp)
    db.session.commit()
    flash("Successfully deleted campaign","success")

    return redirect(url_for('spon_home'))