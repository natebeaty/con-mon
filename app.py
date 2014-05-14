from flask import Flask,render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin
from datetime import date
from marshmallow import Serializer, fields, pprint
import os
basedir = os.path.abspath(os.path.dirname(__file__))

from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.sqla import filters

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
db = SQLAlchemy(app)

app.debug = True

class Convention(db.Model):
		id = db.Column(db.Integer, primary_key=True)
		title = db.Column(db.String(120))
		url = db.Column(db.String(120))
		body = db.Column(db.Text)

		def __unicode__(self):
				return self.title

class Condate(db.Model):
		id = db.Column(db.Integer, primary_key=True)
		title = db.Column(db.String(80))
		body = db.Column(db.Text)
		start_date = db.Column(db.Date)
		end_date = db.Column(db.Date)
		registration_opens = db.Column(db.Date)

		convention_id = db.Column(db.Integer, db.ForeignKey('convention.id'))
		convention = db.relationship('Convention',
				backref=db.backref('conventions', lazy='dynamic'))

		def __unicode__(self):
				return self.title

class ConventionSerializer(Serializer):
	class Meta:
	    fields = ('id', 'title', 'body', 'url')

class CondateSerializer(Serializer):
	convention = fields.Nested(ConventionSerializer)
	class Meta:
	    fields = ('id', 'title', 'body', 'start_date', 'end_date', 'registration_opens')


admin = Admin(app)
admin.add_view(ModelView(Convention, db.session))
admin.add_view(ModelView(Condate, db.session))

@app.route('/')
def index():
	return render_template('index.html',
		condates = Condate.query.filter(Condate.start_date >= date.today()).all()
		)

@app.route('/condates.json')
def condates():
	condates = Condate.query.filter(Condate.start_date >= date.today()).all()
	return CondateSerializer(condates, many=True).json

if __name__ == '__main__':
		app.run(host='0.0.0.0')
