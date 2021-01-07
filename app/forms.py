from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, \
IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User, Pool


class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember')
	submit = SubmitField('Sign_in')

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField('Password2', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Enregistre')
	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Username déjà utilisé')
	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Email déjà utilisé')

class PoolForm(FlaskForm):
	name = StringField('Nom du pool', validators=[DataRequired()])
	pooler = SelectField('Poolers')
	nb_joueur = IntegerField('Nombre de joueurs par Équipe')
	add = SubmitField('ajoute')
	creer = SubmitField('creer')
	def validate_name(self, name):
		pool = Pool.query.filter_by(name=name.data).first()
		if pool is not None:
			raise ValidationError('Nom déjà utilisé; essayer à nouveau')

class PecheForm(FlaskForm):
	joueurs = SelectField('Joueurs disponibles')
	pooler = SelectField('Poolers')
	nb_joueur = IntegerField('Nombre de joueurs par Équipe')
	select = SubmitField('sélectionne')
	complet = SubmitField('fermer le repêchage')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Demande la réinitialisation du mot de passe')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repète Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('réinitialisation')

class ModUsager(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	nouveaupass = PasswordField('Nouveau Password')
	nouveaupass2 = PasswordField('Nouveau Password2', validators=[EqualTo('nouveaupass')])
	submit = SubmitField('Enregistre')

class Admin(FlaskForm):
	pool = SelectField('pool')
	selection = SelectField('selection')
	approuve_pool = SubmitField('Approuve le pool')
	routine = SubmitField('Execute routine de mis a jour')