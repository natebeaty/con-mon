from flask import Flask,render_template
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime, date
from marshmallow import Serializer, fields, pprint
from flask.ext.superadmin import Admin, expose, BaseView, model

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

### models

tags_conventions = db.Table('tags_conventions',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('convention_id', db.Integer, db.ForeignKey('convention.id'))
)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))

    def __unicode__(self):
        return self.title

class Convention(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    url = db.Column(db.String(120))
    body = db.Column(db.Text)
    tags = db.relationship('Tag', secondary=tags_conventions,
        backref=db.backref('conventions', lazy='dynamic'))

    def __unicode__(self):
        return self.title

class Condate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    registration_opens = db.Column(db.Date)
    registration_closes = db.Column(db.Date)

    convention_id = db.Column(db.Integer, db.ForeignKey('convention.id'))
    convention = db.relationship('Convention',
        backref=db.backref('conventions', lazy='dynamic'))

    def __unicode__(self):
        return self.title

### json serialization

class TagSerializer(Serializer):
    class Meta:
        fields = ('id', 'title')

class ConventionSerializer(Serializer):
    tags = fields.Nested(TagSerializer)
    class Meta:
        fields = ('id', 'title', 'body', 'url')

class CondateSerializer(Serializer):
    convention = fields.Nested(ConventionSerializer)
    class Meta:
        fields = ('id', 'title', 'body', 'start_date', 'end_date')

### filters

@app.template_filter()
def timeaway(dt, default="tomorrow"):
    """
    Returns string representing "time away" e.g.
    3 days away, 5 hours away etc.
    """

    now = datetime.utcnow().date()
    diff = dt - now

    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
    )

    for period, singular, plural in periods:

        if period:
            return "%d %s away" % (period, singular if period == 1 else plural)

    return default

@app.template_filter()
def in_past(dt):
    now = datetime.utcnow().date()
    return dt < now

### main views

@app.route('/')
def index():
    return render_template('index.html',
        tags = Tag.query.all(),
        settings = app.config,
        condates = Condate.query.filter(Condate.start_date >= date.today()).order_by(Condate.start_date).all()
        )

@app.route('/condates.json')
def condates():
    condates = Condate.query.filter(Condate.start_date >= date.today()).order_by(Condate.start_date).all()
    return CondateSerializer(condates, many=True).json

### admin views

class ConventionAdmin(model.ModelAdmin):
    session = db.session
    fields = list_display = ('title', 'body', 'url', 'tags')

class TagAdmin(model.ModelAdmin):
    session = db.session
    fields = list_display = ('title',)

class CondateAdmin(model.ModelAdmin):
    session = db.session
    fields = ('convention', 'title', 'start_date', 'end_date', 'registration_opens', 'registration_closes')
    list_display = ('title', 'start_date', 'end_date', 'registration_opens', 'registration_closes')

admin = Admin(app)
admin.register(Convention, ConventionAdmin)
admin.register(Condate, CondateAdmin)
admin.register(Tag, TagAdmin)

### fire up the mothership

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
