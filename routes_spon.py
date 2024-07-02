from flask import render_template,session,send_file,redirect,url_for,request,flash
from main import app
from model import Ad_request, Sponsor,Campaign,db
from wrappers import sponsor_required
from datetime import datetime
import io


@app.route('/home/sponsor')
@sponsor_required
def spon_home():
    spon=Sponsor.query.filter_by(id=session['userId']).first()
    cover_photo= url_for('get_cover_photo', sponsor_id=spon.id)

    campaigns=Campaign.query.filter_by(spon_id=spon.id).all()
    requests=Ad_request.query.filter_by(spon_id=spon.id).all()

    return render_template('sponsor/home_spon.html', active='home', spon=spon,cover_photo=cover_photo,campaigns=campaigns,requests=requests)

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
        )
        db.session.add(campaign)
        db.session.commit()
        # return redirect(url_for('spon_view_camp',camp_id=campaign.id))
        return redirect(url_for('spon_view_camp'))

@app.route('/sponsor/view_campaign')
@sponsor_required
def spon_view_camp():
    # camp = Campaign.query.filter_by(id=camp_id).first()
    return render_template('sponsor/view_camp.html', active='campaigns', camp={})

@app.route('/find/sponsor')
@sponsor_required
def spon_find():
    return render_template('sponsor/find.html', active='find')

@app.route('/stats/sponsor')
@sponsor_required
def spon_stats():
    return render_template('sponsor/stats.html', active='stats')