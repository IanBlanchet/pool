from app import app, db
from app.models import User, Joueur, Pool, Selection
from flask import request
import pandas as pd

@app.route("/detJoueur", methods=["GET", "POST"])
def detJoueur():

	result = Selection.query.filter((Selection.user_id ==1) & (Selection.pool_id ==27)).all()
	demande = request.get_json()
	nb_choix = demande.get('selection')
	return {'test':result[nb_choix].stats.nom}



@app.route("/affImage", methods=["GET", "POST"])
def affImage():

	demande= request.get_json()
	Nom_joueur=demande.get('selection')
	print(Nom_joueur)

	select_joueur = Joueur.query.filter(Joueur.nom.like('%'+Nom_joueur+'%')).first()
	print(select_joueur.alias)
	stats_detail = pd.read_html("https://www.hockey-reference.com/players/"+select_joueur.alias[0]+"/"+select_joueur.alias+".html", header=1)[0]
	detail = pd.DataFrame(stats_detail)
	detail_json = detail.to_json()
	print(detail_json)
	

		
	return {"test":select_joueur.alias, "stats":detail_json}