from flask_mail import Message
from app import app
from app import mail
from flask import render_template

def send_email(sujet, sender, recipients, text_body, html_body):
	msg = Message(sujet, sender=sender, recipients=recipients)
	msg.body = text_body
	msg.html= html_body
	mail.send(msg)

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Pool 2021] Reset Your Password', sender=app.config['ADMINS'][0],\
    	recipients=[user.email],text_body=render_template('email/reset_password.txt',\
    		user=user, token=token),html_body=render_template('email/reset_password.html',\
    		user=user, token=token))

def pool_appro(poolers, pool):
	for user in poolers:
		send_email('[un nouveau pool]',sender=app.config['ADMINS'][0],\
		recipients=[user[1]],text_body=render_template('email/pool_appro.txt',\
			user=user[0], pool=pool),html_body=render_template('email/pool_appro.html',\
			user=user[0], pool=pool))

def accueil_pooler(user):
	send_email('[Pool Père-Fils] Bienvenue', sender=app.config['ADMINS'][0],\
    	recipients=[user.email],text_body=render_template('email/accueil.txt',\
    		user=user),html_body=render_template('email/accueil.html',\
    		user=user))
