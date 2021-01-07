from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
import pandas as pd
from time import time
import jwt
from app import app

@login.user_loader
def load_user(id):
	return User.query.get(int(id))


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	pool = db.relationship('Selection', backref='poolers', lazy='dynamic')
	def __repr__(self):
		return "{} -- {}".format(self.id, self.Nom)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def get_reset_password_token(self, expires_in=600):
		return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, app.config['SECRET_KEY'], algorithm='HS256')

	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
		except:
			return
		return User.query.get(id)


class Joueur(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	alias = db.Column(db.String(9), index=True)
	nom = db.Column(db.String(64), index=True)
	position = db.Column(db.String(2), index=True)
	grandeur = db.Column(db.Float, index=True)
	age = db.Column(db.Integer, index=True)
	equipe = db.Column(db.String(64), index=True)
	pool = db.relationship('Selection', backref='stats', lazy='dynamic')


class Pool(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), index=True, unique=True)
	poolers =  db.Column(db.String(256))
	creation =  db.Column(db.Date)
	selectionneur = db.Column(db.String(64))
	statut = db.Column(db.String(16), default='en_appro')
	pool = db.relationship('Selection', backref='pools', lazy='dynamic')

class Selection(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	joueur_alias =  db.Column(db.String(9), db.ForeignKey('joueur.alias'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	pool_id = db.Column(db.Integer, db.ForeignKey('pool.id'))

#les statitiques des années précédentes
#class2020 = pd.read_excel('class2020.xlsx')

