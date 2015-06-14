from flask import Flask, render_template, request, flash, redirect, url_for, Response
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.sendmail import Mail, Message
from datetime import datetime, date, time, timedelta
from marshmallow import Serializer, fields, pprint
from flask.ext.superadmin import Admin, expose, BaseView, model
from dateutil import parser
from icalendar import Calendar, Event

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
mail = Mail(app)

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
    title = db.Column(db.String(250))
    url = db.Column(db.String(250))
    location = db.Column(db.String(250))
    twitter = db.Column(db.String(250))
    tags = db.relationship('Tag', secondary=tags_conventions,
        backref=db.backref('conventions', lazy='dynamic'))

    def __init__(self, title, location, url):
        self.title = title
        self.location = location
        self.url = url

    def __repr__(self):
        return '<Convention %r>' % self.title

    def __unicode__(self):
        return self.title

class Condate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    notes = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    registration_opens = db.Column(db.Date)
    registration_closes = db.Column(db.Date)
    published = db.Column(db.Boolean)

    convention_id = db.Column(db.Integer, db.ForeignKey('convention.id'))
    convention = db.relationship('Convention',
        backref=db.backref('conventions', lazy='dynamic'))

    def __init__(self, convention_id, title, start_date, end_date, registration_opens, registration_closes, notes):
        self.convention_id = convention_id
        self.title = title
        self.start_date = start_date
        self.end_date = end_date
        self.registration_opens = registration_opens
        self.registration_closes = registration_closes
        self.notes = notes
        self.published = False

    def __repr__(self):
        return '<Condate %r>' % self.title

    def __unicode__(self):
        return self.title

### json serialization

class TagSerializer(Serializer):
    class Meta:
        fields = ('id', 'title')

class ConventionSerializer(Serializer):
    tags = fields.Nested(TagSerializer, many=True)
    class Meta:
        fields = ('id', 'title', 'location', 'url', 'tags')

class CondateSerializer(Serializer):
    convention = fields.Nested(ConventionSerializer)
    class Meta:
        fields = ('id', 'title', 'notes', 'start_date', 'end_date', 'convention')

### template filters

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
        conventions = Convention.query.order_by(Convention.title).all(),
        tags = Tag.query.all(),
        settings = app.config,
        condates = Condate.query.filter(Condate.start_date >= date.today(), Condate.published == True).order_by(Condate.start_date).all()
        )

@app.route('/condates.ics')
def condates_ics():
    condates = Condate.query.filter(Condate.start_date >= date.today(), Condate.published == True).order_by(Condate.start_date).all()
    cal = Calendar()
    cal.add('prodid','-//Con-Mon cartoonist convention calendar//cons.clixel.com//EN')
    cal.add('version','2.0')
    cal.add('X-WR-CALNAME','Con-Mon cartoonist convention calendar')
    for condate in condates:
        e = Event()
        e.add('summary', condate.title)
        e.add('dtstart', condate.start_date)
        if condate.end_date:
            e.add('dtend', datetime.combine(condate.end_date, time(23, 00)))
        e.add('location',condate.convention.location)
        e.add('url', condate.convention.url)
        cal.add_component(e)

        # any registration dates?
        if condate.registration_opens:
            e = Event()
            e.add('summary', "%s registration opens" % condate.title)
            e.add('dtstart', condate.registration_opens)
            e.add('url', condate.convention.url)
            cal.add_component(e)
        if condate.registration_closes:
            e = Event()
            e.add('summary', "%s registration closes" % condate.title)
            e.add('dtstart', condate.registration_closes)
            e.add('url', condate.convention.url)
            cal.add_component(e)

    return Response(cal.to_ical(), mimetype='text/calendar')

@app.route('/condates.json')
def condates_json():
    condates = Condate.query.filter(Condate.start_date >= date.today(), Condate.published == True).order_by(Condate.start_date).all()
    return CondateSerializer(condates, many=True).json

@app.route('/submit_note', methods=['GET', 'POST'])
def submit_note():
    msg = Message("New con-mon note from %s" % request.form['note_email'],
        sender = "hal@cons.clixel.com",
        reply_to = request.form['note_email'],
        recipients = ["nate@clixel.com"])
    msg.body = "%s\n\nFrom: %s\n" % (request.form['note_body'], request.form['note_email'])
    mail.send(msg)
    flash('Your note was sent ok! Thanks!')
    return redirect(url_for('index'))

@app.route('/submit_condate', methods=['GET', 'POST'])
def submit_condate():
    if request.form['convention'] == 'other':
        convention = Convention.query.filter(Convention.title == request.form['convention_title']).first()
        if not convention:
            convention = Convention(
                request.form['convention_title'], 
                request.form['convention_location'],
                request.form['convention_url']
                )
            db.session.add(convention)
            db.session.commit()
        # any tags for convention?
        if request.form['convention_tags']:
            for tag in request.form.getlist('convention_tags'):
                tag = Tag.query.filter(Tag.id == tag).first()
                convention.tags.append(tag)
    else:
        convention = Convention.query.filter(Convention.id == request.form['convention']).first()

    end_date, registration_opens, registration_close = [None, None, None]
    start_date = parser.parse(request.form['start_date'])
    if request.form['end_date']:
        end_date = parser.parse(request.form['end_date'])
    if request.form['registration_opens']:
        registration_opens = parser.parse(request.form['registration_opens'])
    if request.form['registration_closes']:
        registration_close = parser.parse(request.form['registration_closes'])

    condate = Condate(
        convention.id,
        convention.title + ' ' + request.form['start_date'][:4],
        start_date,
        end_date,
        registration_opens,
        registration_close,
        request.form['notes']
        )
    db.session.add(condate)
    db.session.commit()

    # email details
    submit_msg = "New Condate submission!\n\n"
    submit_msg = submit_msg + "Convention: %s\n" % convention.title
    submit_msg = submit_msg + "Start date: %s\n" % request.form['start_date']
    submit_msg = submit_msg + "End date: %s\n" % request.form['end_date']
    submit_msg = submit_msg + "Registration opens: %s\n" % request.form['registration_opens']
    submit_msg = submit_msg + "Registration closes: %s\n" % request.form['registration_closes']
    if request.form['notes']:
        submit_msg = submit_msg + "\nNotes:\n%s\n" % request.form['notes']
    if request.form['email']:
        submit_msg = submit_msg + "\nSender:\n%s\n" % request.form['email']
    submit_msg = submit_msg + "\n\nEdit Condate: %sadmin/condate/%s/\n" % (request.url_root, condate.id)
    if request.form['convention'] == 'other':
        submit_msg = submit_msg + "Edit Convention: %sadmin/convention/%s/\n" % (request.url_root, convention.id)
    msg = Message("New con-mon submission (%s)" % condate.title,
        sender="hal@cons.clixel.com",
        recipients=["nate@clixel.com"])
    msg.body = submit_msg
    mail.send(msg)
    flash('The condate was submitted ok and is in review!')
    return redirect(url_for('index'))

### admin views

class ConventionAdmin(model.ModelAdmin):
    session = db.session
    fields = list_display = ('title', 'location', 'url', 'twitter','tags')

class TagAdmin(model.ModelAdmin):
    session = db.session
    fields = list_display = ('title',)

class CondateAdmin(model.ModelAdmin):
    session = db.session
    fields = ('convention', 'title', 'start_date', 'end_date', 'registration_opens', 'registration_closes', 'published', 'notes')
    list_display = ('title', 'start_date', 'end_date', 'registration_opens', 'registration_closes', 'published')

admin = Admin(app)
admin.register(Convention, ConventionAdmin)
admin.register(Condate, CondateAdmin)
admin.register(Tag, TagAdmin)

### fire up the mothership

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
