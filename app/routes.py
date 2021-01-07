from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, PoolForm, PecheForm, \
ResetPasswordRequestForm, ResetPasswordForm, ModUsager, Admin
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Joueur, Pool, Selection #class2020
from werkzeug.urls import url_parse
from datetime import date, datetime
import pandas as pd
from app.email import send_password_reset_email, pool_appro
from collections import Counter


@app.route("/login", methods=["GET", "POST"])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm(crsf_enabled=False)
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Mauvais mot de passe')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse('next_page').netloc != '':
			next_page = url_for('home')
		return redirect(next_page)

	return render_template('login.html', form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))


@app.route("/register", methods=["GET", "POST"])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm(crsf_enabled=False)
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		return redirect(url_for('login'))

	return render_template('register.html', form=form)

@app.route("/", methods=["GET", "POST"])
@app.route("/home")
def home():
	user=0
	if current_user.is_authenticated:
		user = current_user.id
	return render_template('index.html', user=user)

@app.route("/<string:username>", methods=["GET", "POST"])
@login_required
#modification d'un usager
def usager(username):
	form=ModUsager(crsf_enabled=False)
	usager_courant = User.query.filter_by(username = username).first()

	if form.nouveaupass.data:
		if form.validate_on_submit():
			usager_courant.set_password(form.nouveaupass.data)
			
			usager_courant.username=form.username.data
			usager_courant.email=form.email.data
			if usager_courant.check_password(form.password.data):
				db.session.commit()
				return redirect(url_for('home'))
			else:
				flash('Mauvais mot de passe')
	else:
		if form.validate_on_submit():
			usager_courant.username=form.username.data
			usager_courant.email=form.email.data
			if usager_courant.check_password(form.password.data):
				db.session.commit()
				return redirect(url_for('home'))
			else:
				flash('Mauvais mot de passe')


	return render_template('mod_usager.html', form=form, usager=usager_courant)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetPasswordRequestForm(crsf_enabled=False)
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	user = User.verify_reset_password_token(token)
	if not user:
		return redirect(url_for('home'))
	form = ResetPasswordForm(crsf_enabled=False)
	if form.validate_on_submit():
		user.set_password(form.password.data)
		db.session.commit()
		return redirect(url_for('login'))
	return render_template('reset_password.html', form=form)




#à réviser afin de créer la liste sur frontend en JS
choix_pooler = []

@app.route("/accueil_pool", methods=["GET", "POST"])
@login_required
def accueil_pool():
	form = PoolForm(crsf_enabled=False)
	form.pooler.choices=[(str(pooler.username)) for pooler in User.query.order_by(User.id).all()]
	lespool = Pool.query.filter(Pool.statut != 'en_appro').all()
	#ajoute un pooler dans le pool
	if form.add.data and form.pooler.data and form.name.data :

		if form.pooler.data not in choix_pooler:
			choix_pooler.append(form.pooler.data)
			nom_pool = form.name.data
			return render_template('accueil_pool.html', form=form, lespool=lespool, choix_pooler=choix_pooler, nom_pool=nom_pool)
		else:
			nom_pool = form.name.data
			return render_template('accueil_pool.html', form=form, lespool=lespool, choix_pooler=choix_pooler, nom_pool=nom_pool)

	#creer le nouveau pool dans la bd
	if form.creer.data and form.name.data:
		if form.validate_on_submit():
		#if form.name.data not in [pool.name for pool in lespool]:
			nouv_pool = Pool(name=form.name.data, poolers=str(choix_pooler), creation=date.today())
			db.session.add(nouv_pool)
			db.session.commit()
			choix_pooler.clear()
			lespool = Pool.query.filter(Pool.statut != 'en_appro').all()
			return render_template('accueil_pool.html', form=form, lespool=lespool, choix_pooler=[])
	choix_pooler.clear()

	return render_template('accueil_pool.html', form=form, lespool=lespool, choix_pooler=choix_pooler)
	

@app.route("/repechage/<int:pool_id>", methods=["GET", "POST"])
@login_required
def repechage(pool_id):

	#extraire les données pertiente
	pool_actif = Pool.query.filter_by(id = pool_id).first()
	joueurs = Joueur.query.all()
	selection = Selection.query.filter_by(pool_id = pool_id).all()
	#count le nombre de choix par pooler
	list_joueur_select = [select.poolers.username for select in selection]
	count_pooler = Counter(list_joueur_select)
	

	#organise le form
	form = PecheForm(crsf_enabled=False)
	choix_joueur = []


	#form.joueurs.choices=[(joueur.nom +' - '+joueur.position+' - '+joueur.equipe) for joueur in joueurs]
	list_poolers = [pooler.strip("' ") for pooler in (pool_actif.poolers.strip('[]').split(','))]
	form.pooler.choices=list_poolers
	nb_pooler = len(list_poolers)


	if form.select.data and form.joueurs.data and form.pooler.data:
		id_joueur = form.joueurs.data.split('-')
		id_joueur = int(id_joueur[0])
		pooler_id = User.query.filter_by(username=form.pooler.data).first()
		joueur_alias = Joueur.query.filter_by(id= id_joueur).first()
		alias = joueur_alias.alias

		

		la_selection = Selection(joueur_alias=alias, user_id=pooler_id.id, pool_id=pool_id )
		db.session.add(la_selection)
		db.session.commit()

	selection = Selection.query.filter_by(pool_id = pool_id).all()
	list_joueur_select = [select.poolers.username for select in selection]
	count_pooler = Counter(list_joueur_select)

	alias_selection = [select.joueur_alias for select in selection]
	choix_joueur.clear()
	for joueur in joueurs:
		if joueur.alias not in alias_selection:
			choix_joueur.append(str(joueur.id) + '- ' + joueur.nom +' - '+joueur.position+' - '+joueur.equipe)
	form.joueurs.choices=choix_joueur
	z = len(selection)
	selection = reversed(selection)
	
	if form.complet.data:
		pool_actif.statut = 'actif'
		db.session.commit()
		return redirect(url_for('accueil_pool'))


	return render_template('repechage.html', form=form, nb_pooler=nb_pooler, pool_actif=pool_actif, \
		selection=selection, counter=count_pooler, z=z)



@app.route("/projection", methods=["GET", "POST"])
@login_required
def projection():
	
		return render_template('projection.html')



@app.route("/monpool/<int:user_id>", methods=["GET", "POST"])
@login_required
def monpool(user_id):

	stats_detail = pd.read_html("https://www.hockey-reference.com/leagues/NHL_2020_skaters.html", header=1)[0]
	detail = pd.DataFrame(stats_detail)
	stats = detail[['Player', 'G', 'A', 'PTS']]
	stats.fillna(0, inplace=True)
	#creer une routine pour accéder seulement au pool de l'usager logger
	
	mes_pools=[]

	for pool in Pool.query.filter_by(statut='actif'):
		if Selection.query.filter((Selection.pool_id == pool.id) & (Selection.user_id==user_id)).first():
			data = Selection.query.join(User).join(Joueur).filter(Selection.pool_id == pool.id).all()
			#selection = pd.read_sql(test.filter_by(pool_id=pool.id).all())
			pool_data = pd.DataFrame(columns=['Joueur', 'Pooler', 'G', 'A', 'PTS'])
			for select in data:
				
				pool_data = pool_data.append({'Joueur':select.stats.nom,'Pooler':select.poolers.username}, ignore_index=True)



			for i in range(len(pool_data)):
				joueur = stats[stats.Player == pool_data.iloc[i,0]]
				try:
					nb_but = int(joueur.G)
					nb_pass = int(joueur.A)
					nb_pts = int(joueur.PTS)
					pool_data.iloc[i,2] = nb_but
					pool_data.iloc[i,3] = nb_pass
					pool_data.iloc[i,4] = nb_pts
				except:
					continue
			sommaire = pool_data.groupby(['Pooler']).sum()
			sommaire.sort_values('PTS',ascending=False,inplace=True)
			sommaire= sommaire[['G', 'A', 'PTS']]
			sommaire = sommaire.reset_index()
			
			
			
			
			mes_pools.append([len(sommaire), pool.name, sommaire])

			
	return render_template('monpool.html', mes_pools=mes_pools)


@app.route("/administration", methods=["GET", "POST"])
@login_required
def administration():

	# code utilisé pour meubler la base de données des joueurs
	'''stats_detail = pd.read_html("https://www.hockey-reference.com/leagues/NHL_2020_skaters.html", header=1)[0]
	detail = pd.DataFrame(stats_detail)
	stat_2020 = detail[['Rk', 'Tm', 'Pos','Player', 'Age', 'G', 'A', 'PTS']]
	stat_2020.fillna(0, inplace=True)
	stat_2020 = stat_2020.drop_duplicates(subset='Rk', keep='last', ignore_index=True)
	stat_2020 = stat_2020[stat_2020.Player != 'Player']
	stat_2020.reset_index(inplace=True, drop=True)
	
	serie_alias = []
	for i in range(len(stat_2020)):
		nom = stat_2020.loc[i,'Player']
		if "-" in nom:
			nom = nom.replace('-', '')
		if "." in nom:
			nom = nom.replace('.', '')
		if "'" in nom:
			nom = nom.replace("'", '')
		if "*" in nom:
			nom = nom.replace("*", '')
		nom_split = nom.split()
		alias = nom_split[1][0:5].lower() + nom_split[0][0:2].lower()
		serie_alias.append(alias)
	stat_2020['alias'] = serie_alias
	stat_2020['duplic'] = stat_2020.duplicated(subset='alias', keep='first')
	serie_num = []
	z=1
	for i in range(len(stat_2020)):
		if stat_2020.loc[i,'duplic'] == False:
			z=1
			serie_num.append(z)
			
		else:
			serie_num.append(z+1)
			z += 1
	stat_2020['num'] = serie_num
	
	for i in range(len(stat_2020)):
		nom= stat_2020.loc[i,'Player']
		position = stat_2020.loc[i,'Pos']
		age = stat_2020.loc[i,'Age']
		equipe = stat_2020.loc[i,'Tm']
		alias = stat_2020.loc[i,'alias'] + '0' + str(stat_2020.loc[i,'num'])
		le_joueur = Joueur(nom=nom, position=position, age=age, equipe=equipe, alias=alias)
		db.session.add(le_joueur)
		db.session.commit()'''

	#valide si c'est moi
	if current_user.username == 'Ian':
		pool_attent = Pool.query.filter_by(statut = 'en_appro').all()
		form = Admin(crsf_enabled=False)
		form.pool.choices=[pool.name for pool in pool_attent]
		
		#approuve un nouveau pool
		if form.pool.data and form.approuve_pool.data:
			#change le statut du pool
			pool_app = Pool.query.filter_by(name=form.pool.data).first()
			pool_app.statut = 'repechage'
			db.session.commit()
			#extrait les poolers du pool
			les_poolers = [pooler.strip("' ") for pooler in pool_app.poolers.strip('[]').split(',')]
			list_email = [User.query.filter_by(username=pooler).first().email for pooler in les_poolers]
			les_poolers = list(zip(les_poolers, list_email))
			#envoi un courriel de confirmation
			pool_appro(les_poolers, pool_app.name)

			pool_attent = Pool.query.filter_by(statut = 'en_appro').all()
			form.pool.choices=[pool.name for pool in pool_attent]

		#lance une routine de mise à jour
		if form.routine.data:


			return redirect(url_for('home'))


		return render_template('admin.html', form=form)


	return redirect(url_for('home'))