from flask import render_template,session,redirect,url_for,request,flash
from wrappers import admin_required
from model import Campaign,Influencer,Ad,Sponsor,db
from datetime import date
from main import app

#! list of routes and its purpose
# 1. admin_home -> loads home page for admin
# 2. plain find page, just renders template
# 3. handles form in find page, takes input text and role and to next function to find it.
# 4. search_all function applies the queries and gives details, another function to accomodate, a tag, href calls.
# 5. inverse -> this flags or unflags the products/roles
# 6. unflag_influ -> to directly unflag from admin home
# 7. unflag_camp -> to directly unflag from admin home
# 8. view_camp -> to directly view from admin home
# 9. view -> gives view to all the products/roles
# 10. admin_stats -> statics page for admin.


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

@app.route('/searchAll/<string:filter_option>', defaults={'search_query': ''}, methods=['GET'])
@app.route('/searchAll/<string:search_query>/<string:filter_option>', methods=['GET'])
def search_all(search_query, filter_option):
    
    if search_query == "":
        if filter_option == 'spon':
            results = Sponsor.query.filter(Sponsor.is_flagged.is_(False)).all()
        elif filter_option == 'influ':
            results = Influencer.query.filter(Influencer.is_flagged.is_(False)).all()
        elif filter_option == 'camps':
            results = Campaign.query.filter(Campaign.is_flagged.is_(False)).all()
        elif filter_option == 'ads':
            results = Ad.query.filter(Ad.is_flagged.is_(False)).all()
        elif filter_option == 'flag_spon':
            results = Sponsor.query.filter(Sponsor.is_flagged).all()
        elif filter_option == 'flag_influ':
            results = Influencer.query.filter(Influencer.is_flagged).all()
        elif filter_option == 'flag_camps':
            results = Campaign.query.filter(Campaign.is_flagged).all()
        elif filter_option == 'flag_ads':
            results = Ad.query.filter(Ad.is_flagged).all()
        else:
            results = []
    else:
        if filter_option == 'spon':
            results = Sponsor.query.filter(Sponsor.name.contains(search_query),Sponsor.is_flagged.is_(False)).all()
        elif filter_option == 'influ':
            results = Influencer.query.filter(Influencer.name.contains(search_query),Influencer.is_flagged.is_(False)).all()
        elif filter_option == 'camps':
            results = Campaign.query.filter(Campaign.name.contains(search_query),Campaign.is_flagged.is_(False)).all()
        elif filter_option == 'ads':
            results = Ad.query.filter(Ad.name.contains(search_query),Ad.is_flagged.is_(False)).all()
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
    
    if(results==[]):
        flash("No suitable search found","danger")
    return render_template('admin/find_admin.html', active="find", search_query=search_query, filter_option=filter_option, results=results)

@app.route('/inverse/<int:id>/<string:role>')
def inverse(id, role):

    if role == "camps" or role == "flag_camps":
        res = Campaign.query.filter_by(id=id).first()
    elif role == "ads" or role == "flag_ads":
        res = Ad.query.filter_by(id=id).first()
    elif role == "spon" or role == "flag_spon":
        res = Sponsor.query.filter_by(id=id).first()
    elif role == "influ" or role == "flag_influ":
        res = Influencer.query.filter_by(id=id).first()
    else:
        return redirect(url_for('search_all', filter_option=role))

    if res:
        res.is_flagged = not res.is_flagged
        db.session.commit()
    flash("Operation Successful", "success")
    return redirect(url_for('search_all', filter_option=role))


@app.route('/unflag_influ/<int:id>')
def unflag_influ(id):
    influ = Influencer.query.filter_by(id=id).first()
    if influ:
        influ.is_flagged = False
        db.session.commit()
    return redirect(url_for('admin_home'))

@app.route('/unflag_camp/<int:id>')
def unflag_camp(id):
    camp = Campaign.query.filter_by(id=id).first()
    if camp:
        camp.is_flagged = False
        db.session.commit()
    return redirect(url_for('admin_home'))

@app.route('/view/<int:campaign_id>')
def view_campaign(campaign_id):
    camp = Campaign.query.get_or_404(campaign_id)
    spon=Sponsor.query.get(camp.spon_id)
    ads = Ad.query.filter_by(spon_id=camp.spon_id).all()
    return render_template('admin/view.html', active="home",view="campaign",camp=camp,spon=spon,ads=ads)

@app.route('/viewAll/<int:id>/<string:role>')
def view(id,role):
    camp,spon,ads,influ = [],[],[],[]
    view = ""

    if role == "camps" or role == "flag_camps":
        camp = Campaign.query.get_or_404(id)
        spon=Sponsor.query.get(camp.spon_id)
        ads = Ad.query.filter_by(campaign_id=camp.id).all()
        view="campaign"
    elif role == "ads" or role == "flag_ads":
        ads = Ad.query.get(id)
        view='ad'
    elif role == "spon" or role == "flag_spon":
        spon = Sponsor.query.get(id)
        view="sponsor"
    elif role == "influ" or role == "flag_influ":
        influ = Influencer.query.get(id)
        view='influ'
    else:
        return redirect(url_for('search_all', filter_option=role))

    return render_template('admin/view.html', active="find",view=view,camp=camp,spon=spon,ad=ads,influ=influ)
 
    # spon=Sponsor.query.get(camp.spon_id)
    # ads = Ad.query.filter_by(spon_id=camp.spon_id).all()



@app.route('/statsAll')
@admin_required
def admin_stats():
    sponsors = Sponsor.query.all()

    labels = []
    data = []

    for sponsor in sponsors:
        campaign_count = Campaign.query.filter_by(spon_id=sponsor.id).count()
        labels.append(sponsor.name)
        data.append(campaign_count)

    labels_data = sorted(zip(labels, data), key=lambda x: x[1], reverse=True)
    labels, data = zip(*labels_data)

    return render_template('admin/stats.html', active='stats', labels=labels, data=data)