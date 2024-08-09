from flask import render_template,session,send_file,redirect,url_for,request,flash
from sqlalchemy import desc
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


@app.route('/home/sponsor')
@sponsor_required
def spon_home():
    spon=Sponsor.query.filter_by(id=session['userId']).first()
    cover_photo= url_for('get_cover_photo', sponsor_id=spon.id)
    current_date = date.today()

    campaigns=Campaign.query.filter(Campaign.spon_id==spon.id,Campaign.start_date < current_date, Campaign.end_date > current_date).all()
    requests = db.session.query(Ad_request, Influencer.name.label('influ_name')).\
    join(Influencer, Ad_request.influ_id == Influencer.id).\
    filter(Ad_request.spon_id == spon.id, Ad_request.sender == "influencer").all()

    pen_requests = db.session.query(Ad_request, Influencer.name.label('influ_name')).\
    join(Influencer, Ad_request.influ_id == Influencer.id).\
    filter(Ad_request.spon_id == spon.id, Ad_request.sender == "sponsor").all()

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
    closed_camp=Campaign.query.filter(Campaign.spon_id==spon.id, Campaign.end_date < current_date).all()
    flagged_camp=Campaign.query.filter(Campaign.spon_id==spon.id, Campaign.is_flagged == True).all()

    return render_template('sponsor/campaigns.html', active='campaigns',live_campaigns=live_camp, closed_campaigns=closed_camp, flagged_camp=flagged_camp)

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
            description=desc,
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
    return render_template('sponsor/view_camp.html', active='campaigns', camp=camp,ads=ads)

@app.route('/sponsor/view_ad/<int:ad_id>')
def spon_view_ad(ad_id):
    ad = Ad.query.filter_by(id=ad_id).first()
    return render_template('sponsor/view_camp.html', active='campaigns', ads=ad)


@app.route('/sponsor/add_ad')
def spon_add_ad():
    ad={}
    return render_template('sponsor/add_ad.html', active='campaigns',ad=ad, showInfluencers=False)

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

    print("this is name and budget", name, budget)

    if(name == "" or budget == "" or name == None or budget == None):
        flash("Please fill in all the fields","danger")
        return redirect(url_for('spon_add_ad'))
    
    ad_req = Ad_request(
        ad_name=name,
        influ_id=influencer_id,
        spon_id=session['userId'],
        amount=budget,
        comments=comments,
        sender="sponsor",
        previous_request_id=None,
    )

    db.session.add(ad_req)
    db.session.commit()
    return redirect(url_for('spon_home'))
















@app.route('/find/sponsor/Ads')
@sponsor_required
def spon_find_Ads():
    return render_template('sponsor/find_ads.html', active='find' , findActive="ads")

@app.route('/find/sponsor/Camp')
@sponsor_required
def spon_find_Camp():
    return render_template('sponsor/find_camp.html', active='find', findActive="camp")

@app.route('/find/sponsor')
@sponsor_required
def spon_find():
    return render_template('sponsor/find_influ.html', active='find', findActive="influ")

@app.route('/stats/sponsor')
@sponsor_required
def spon_stats():
    return render_template('sponsor/stats.html', active='stats')
