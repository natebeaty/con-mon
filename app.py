from flask import Flask, render_template, request, flash, redirect, url_for, Response, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime, date, time, timedelta
from marshmallow import Schema, fields, pprint
from flask_superadmin import Admin, expose, BaseView, AdminIndexView as _AdminIndexView
from flask_superadmin.model import ModelAdmin as _ModelAdmin
from dateutil import parser
from icalendar import Calendar, Event
from functools import wraps
import uuid
import re
import config

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

    def __repr__(self):
        return self.title

class Convention(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    url = db.Column(db.String(250))
    location = db.Column(db.String(250))
    twitter = db.Column(db.String(250))
    condates = db.relationship('Condate',
        backref=db.backref('condates'))
    tags = db.relationship('Tag', secondary=tags_conventions,
        backref=db.backref('conventions', lazy='dynamic'))
    archived = db.Column(db.Boolean)

    def __repr__(self):
        return self.title

class Condate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    notes = db.Column(db.Text)
    public_notes = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    registration_opens = db.Column(db.Date)
    registration_closes = db.Column(db.Date)
    published = db.Column(db.Boolean)
    cancelled = db.Column(db.Boolean)
    submission_hash = db.Column(db.String(250))

    convention_id = db.Column(db.Integer, db.ForeignKey('convention.id'))
    convention = db.relationship('Convention',
        backref=db.backref('conventions', lazy='dynamic'))

    def __repr__(self):
        return self.title

class Phrase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(250))
    num_uses = db.Column(db.Integer)

    def __repr__(self):
        return self.body


### json serialization

class TagSchema(Schema):
    class Meta:
        fields = ('id', 'title')

class ConventionSchema(Schema):
    tags = fields.Nested(TagSchema, many=True)
    class Meta:
        fields = ('id', 'title', 'location', 'url', 'tags', 'archived')

class CondateSchema(Schema):
    convention = fields.Nested(ConventionSchema)
    class Meta:
        fields = ('id', 'title', 'notes', 'start_date', 'end_date', 'convention')


### template filters

@app.template_filter()
def timeaway(dt, default='tomorrow'):
    """
    Returns string representing "time away" e.g.
    3 days away, 5 hours away etc.
    """

    now = datetime.utcnow().date()
    diff = dt - now

    if diff.days == 0:
        return ''

    periods = (
        (diff.days / 30, 'month', 'months'),
        # (diff.days / 7, 'week', 'weeks'),
        (diff.days, 'day', 'days'),
    )

    for period, singular, plural in periods:
        if period >= 1:
            return '%s%d %s' % ('~' if singular != 'day' else '', period, singular if period < 2 else plural)

    return default

@app.template_filter()
def in_past(dt):
    """
    Returns true if datetime in past
    """
    now = datetime.utcnow().date()
    return dt < now

@app.template_filter()
def is_past_or_today(dt):
    """
    Returns true if datetime in past
    or today
    """
    now = datetime.utcnow().date()
    return dt <= now

@app.template_filter()
def away_tags(dt):
    """
    Returns a string of tags for
    styling (not currently used)
    """
    output = ''
    if dt > date.today() + timedelta(30):
        output += ' month-away'
    if dt > date.today() + timedelta(60):
        output += ' two-months-away'
    if dt > date.today() + timedelta(90):
        output += ' far-away'
    return output

### main views

@app.route('/')
def index():
    """
    Homepage view
    """
    return render_template('index.html',
        conventions = Convention.query.order_by(Convention.title).all(),
        tags = Tag.query.all(),
        settings = app.config,
        condates = Condate.query.filter(Condate.start_date >= date.today(), Condate.published == True).order_by(Condate.start_date).all()
        )

@app.route('/condates.ics')
def condates_ics():
    """
    Pull active condates for calendar
    subscriptions in ics format
    """
    condates = Condate.query.filter(Condate.start_date >= date.today(), Condate.published == True).order_by(Condate.start_date).all()
    cal = Calendar()
    cal.add('prodid','-//Con-Mon//con-mon.com//EN')
    cal.add('version','2.0')
    cal.add('X-WR-CALNAME','Con-Mon')
    for condate in condates:
        e = Event()
        title = condate.title
        # append public_notes to title
        if condate.cancelled and condate.public_notes:
            title += ' (%s)' % re.sub('<[^<]+?>', '', condate.public_notes)
        # set status to cancelled?
        if condate.cancelled:
            e.add('status', 'CANCELLED')
        e.add('summary', title)
        e.add('dtstart', condate.start_date)
        if condate.end_date:
            e.add('dtend', datetime.combine(condate.end_date, time(23, 00)))
        e.add('location',condate.convention.location)
        e.add('url', condate.convention.url)
        cal.add_component(e)

        # any registration dates?
        if condate.registration_opens:
            e = Event()
            e.add('summary', '%s registration opens' % condate.title)
            e.add('dtstart', condate.registration_opens)
            e.add('url', condate.convention.url)
            cal.add_component(e)
        if condate.registration_closes:
            e = Event()
            e.add('summary', '%s registration closes' % condate.title)
            e.add('dtstart', condate.registration_closes)
            e.add('url', condate.convention.url)
            cal.add_component(e)

    return Response(cal.to_ical(), mimetype='text/calendar')

@app.route('/condates.json')
def condates_json():
    """
    Pull condates in json for
    clndr view on homepage
    """
    condates = Condate.query.filter(Condate.start_date >= date.today(), Condate.published == True, Condate.cancelled == False).order_by(Condate.start_date).all()
    result = CondateSchema(many=True).dump(condates)
    return jsonify({'condates': result})

@app.route('/condates', methods=['GET'])
def condates():
    """
    All Condates view
    """
    return render_template('condates.html',
        conventions = Convention.query.order_by(Convention.title).all(),
        tags = Tag.query.all(),
        settings = app.config,
        all_condates = Condate.query.filter(Condate.published == True).order_by(Condate.start_date).all(),
        current_condates = Condate.query.filter(Condate.start_date >= date.today(), Condate.published == True).order_by(Condate.start_date).all()
        )

@app.route('/submit_note', methods=['POST'])
def submit_note():
    """
    Submit note (not currently used)
    """
    msg = Message('New con-mon note from %s' % request.form['note_email'],
        sender = 'hal@con-mon.com',
        reply_to = request.form['note_email'],
        recipients = ['nate@clixel.com'])
    msg.body = '%s\n\nFrom: %s\n' % (request.form['note_body'], request.form['note_email'])
    mail.send(msg)
    flash('Your note was sent ok! Thanks!')
    return redirect(url_for('index'))

@app.route('/approve_condate', methods=['GET'])
def approve_condate():
    """
    Approve condate from email link
    (hash generated on submission)
    """
    condate = Condate.query.filter(Condate.submission_hash == request.args.get('hash')).one()
    if (condate):
        condate.published = True
        db.session.commit()
        flash('Condate approved ok! <a href="/admin/condate/%s/">Edit Condate</a>' % condate.id)
    return redirect(url_for('index'))

@app.route('/submit_condate', methods=['POST'])
def submit_condate():
    """
    User submission of new condate (yay!)
    """
    start_date = request.form.get('start_date', '')
    if request.form.get('diebots_5000', None) or start_date == '' or start_date == str(datetime.now())[:10]:
        if request.is_xhr:
            return jsonify({ 'message': 'Suspected as spam.' })
        else:
            flash('Suspected as spam.')
            return redirect(url_for('index'))

    convention_id = request.form.get('convention', None)
    if not convention_id:
        return jsonify({ 'message': 'Bad request' })
    elif convention_id == 'other':
        convention = Convention.query.filter(Convention.title == request.form.get('convention_title', '')).first()
        if not convention:
            twitter_handle = request.form.get('convention_twitter', '').replace('@','')
            convention = Convention(
                title = request.form.get('convention_title', ''),
                twitter = twitter_handle,
                location = request.form.get('convention_location', ''),
                url = request.form.get('convention_url', '')
                )
            db.session.add(convention)
            db.session.commit()
        # any tags for convention?
        if request.form.get('convention_tags', None):
            for tag in request.form.getlist('convention_tags'):
                tag = Tag.query.filter(Tag.id == tag).first()
                convention.tags.append(tag)
    else:
        convention = Convention.query.filter(Convention.id == convention_id).first()

    notes = request.form.get('notes', '')
    email = request.form.get('email', None)
    if email:
        notes = '%s (submitted by %s)' % (notes, email)
    title = convention.title + ' ' + start_date[:4]
    condate = Condate(
        convention_id = convention.id,
        title = title,
        start_date = parser.parse(start_date),
        notes = notes,
        published = False,
        cancelled = False,
        submission_hash = uuid.uuid4().hex
        )

    # optional dates
    registration_opens = request.form.get('registration_opens', None)
    registration_closes = request.form.get('registration_closes', None)
    end_date = request.form.get('end_date', None)
    if end_date:
        condate.end_date = parser.parse(end_date)
    if registration_opens:
        condate.registration_opens = parser.parse(registration_opens)
    if registration_closes:
        condate.registration_closes = parser.parse(registration_closes)

    db.session.add(condate)
    db.session.commit()

    # email details
    submit_msg = 'New Condate submission!\n\n'
    submit_msg = submit_msg + 'Convention: %s\n' % convention.title
    submit_msg = submit_msg + 'Start date: %s\n' % condate.start_date
    submit_msg = submit_msg + 'End date: %s\n' % condate.end_date
    submit_msg = submit_msg + 'Registration opens: %s\n' % condate.registration_opens
    submit_msg = submit_msg + 'Registration closes: %s\n' % condate.registration_closes
    if notes:
        submit_msg = submit_msg + '\nNotes:\n%s\n' % notes
    if email:
        submit_msg = submit_msg + '\nSender:\n%s\n' % email
        reply_to = email
    else:
        reply_to = ''
    submit_msg = submit_msg + '\n\nEdit Condate: %sadmin/condate/%s/\n' % (request.url_root, condate.id)
    submit_msg = submit_msg + 'Approve: %sapprove_condate?hash=%s\n' % (request.url_root, condate.submission_hash)
    if convention_id == 'other':
        submit_msg = submit_msg + 'Edit Convention: %sadmin/convention/%s/\n' % (request.url_root, convention.id)
    msg = Message('New con-mon submission (%s)' % condate.title,
        sender = 'hal@con-mon.com',
        reply_to = reply_to,
        recipients = ['nate@clixel.com'])
    msg.body = submit_msg
    mail.send(msg)

    if request.is_xhr:
        return jsonify({
            'success': True,
            'message': 'The condate was submitted ok and is in review!'
            })
    else:
        flash('The condate was submitted ok and is in review!')
        return redirect(url_for('index'))

### admin views


# basic auth
def check_auth(username, password):
    return username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD

def authenticate():
    return Response(
    'Oops you did not log in ok.', 401,
    { 'WWW-Authenticate': 'Basic realm="Login Required"' })

def is_authenticated():
    auth = request.authorization
    return auth and check_auth(auth.username, auth.password)


class ModelAdmin(_ModelAdmin):

    def is_accessible(self):
        return is_authenticated()

    def _handle_view(self, name, *args, **kwargs):
        if not self.is_accessible():
            return authenticate()

class AdminIndexView(_AdminIndexView):
    @expose('/')
    def index(self):
        if not is_authenticated():
            return authenticate()
        return self.render('admin/index.html')
        # return super(AdminIndexView, self).index()

class ConventionAdmin(ModelAdmin):
    session = db.session
    fields = list_display = ('title', 'location', 'url', 'twitter', 'tags', 'archived',)

class TagAdmin(ModelAdmin):
    session = db.session
    fields = list_display = ('title',)

class CondateAdmin(ModelAdmin):
    session = db.session
    fields = ('convention', 'title', 'start_date', 'end_date', 'registration_opens', 'registration_closes', 'published', 'cancelled', 'notes', 'public_notes', 'submission_hash',)
    list_display = ('title', 'start_date', 'end_date', 'registration_opens', 'registration_closes', 'published', 'cancelled', )

class PhraseAdmin(ModelAdmin):
    session = db.session
    fields = list_display = ('body','num_uses',)

admin = Admin(app, index_view=AdminIndexView(), name='Con Mon')
admin.register(Convention, ConventionAdmin)
admin.register(Condate, CondateAdmin)
admin.register(Tag, TagAdmin)
admin.register(Phrase, PhraseAdmin)

### fire up the mothership

if __name__ == '__main__':
    app.run(host='0.0.0.0')
    # app.run(host='0.0.0.0', port=8080)
