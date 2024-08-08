from flask import render_template,session,redirect,url_for,request
from wrappers import admin_required
from model import User,Campaign,Influencer,Ad,Sponsor
from datetime import date
from main import app


@app.route('/home')
@admin_required
def admin_home():
    current_date = date.today()

    camps = Campaign.query.filter( Campaign.end_date > current_date).all()
    flag_users = Influencer.query.filter(Influencer.is_flagged).all()
    flag_camps = Campaign.query.filter(Campaign.is_flagged).all()
    return render_template('admin/home_admin.html', active='home',user=session['username'],campaigns=camps,flag_users=flag_users,flag_campaigns=flag_camps)


@app.route('/findAll')
@admin_required
def admin_find():
    return render_template('admin/find_admin.html', active='find')


@app.route('/findAll', methods=['POST'])
@admin_required
def admin_find_post():
    search_query = request.form.get('searchAll')
    filter_option = request.form.get('filter_html')    
    return redirect(url_for('search_all', search_query=search_query, filter_option=filter_option))

@app.route('/searchAll/<string:search_query>/<string:filter_option>', methods=['GET'])
def search_all(search_query, filter_option):
    
    if filter_option == 'spon':
        results = Sponsor.query.filter(Sponsor.name.contains(search_query)).all()
    elif filter_option == 'influ':
        results = Influencer.query.filter(Influencer.name.contains(search_query)).all()
    elif filter_option == 'camps':
        results = Campaign.query.filter(Campaign.name.contains(search_query)).all()
    elif filter_option == 'ads':
        results = Ad.query.filter(Ad.name.contains(search_query)).all()
    elif filter_option == 'flag_spon':
        results = Sponsor.query.filter(Sponsor.name.contains(search_query), Sponsor.is_flagged).all()
    elif filter_option == 'flag_influ':
        results = Influencer.query.filter(Influencer.name.contains(search_query), Influencer.is_flagged).all()
    elif filter_option == 'flag_camps':
        results = Campaign.query.filter(Campaign.name.contains(search_query), Campaign.is_flagged).all()
    elif filter_option == 'flag_ads':
        results = Ad.query.filter(Ad.name.contains(search_query), Ad.is_flagged).all()
    else:
        results = []

    return render_template('admin/find_admin.html',active="find", search_query=search_query, filter_option=filter_option, results=results)


@app.route('/flag/<int:id>')
def flag(id):
    return redirect(url_for('admin_stats'))

@app.route('/statsAll')
@admin_required
def admin_stats():
    return render_template('admin/stats.html', active='stats')

@app.route('/view/<int:campaign_id>')
def view_campaign(campaign_id):
    camp = Campaign.query.get_or_404(campaign_id)
    return render_template('admin/view_camp.html', active="home",view="campaign",camp=camp,spon=[],ads=[])

    # spon=Sponsor.query.get(camp.spon_id)
    # ads = Ad.query.filter_by(spon_id=camp.spon_id).all()