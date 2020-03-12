from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager,Command
from datetime import date, datetime, timedelta
from app import Condate,Tag,Phrase
import config
import twitter
import random

app = Flask(__name__)
app.config.from_object('config')
manager = Manager(app)
db = SQLAlchemy(app)

class Twitter(Command):
    """
    Twitter alerts!
    Weekly and monthly notices of approaching convention dates
    Weekly notices of approaching registration deadlines
    """

    def post_to_twitter(self,twitter_api,message):
        try:
            twitter_api.PostUpdate(message)
            return ''
        except:
            return "There was an error posting '%s' to twitter. Please write Nate and mock him." % message

    def run(self):
        twitter_api = twitter.Api(consumer_key=config.TWITTER_CONSUMER_KEY, consumer_secret=config.TWITTER_CONSUMER_SECRET, access_token_key=config.TWITTER_ACCESS_TOKEN_KEY, access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET)
        indie_tag = Tag.query.filter(Tag.title == "Indie").first()

        # get least used phrases pool
        min_uses = db.session.query(db.func.min(Phrase.num_uses)).scalar()
        phrases = Phrase.query.filter(Phrase.num_uses == min_uses).all()

        # cons that are a week away
        daily_notices = Condate.query.filter(Condate.start_date == date.today() + timedelta(days=7), Condate.published == True, Condate.cancelled == False).all()
        output = "Condates happening in a week: \n"
        for c in daily_notices:
            if indie_tag in c.convention.tags:
                phrase = random.choice(phrases)
                # update phrase num_uses count & remove from pool
                phrase.num_uses += 1
                phrases.remove(phrase)
                message = "%s %s is a week away. %s" % (phrase, c.convention.title, c.convention.url)
                if c.convention.twitter:
                    message = message + " @%s" % (c.convention.twitter)
                output = output + self.post_to_twitter(twitter_api,message) + "\n" + message

        # cons that are a month away
        monthly_notices = Condate.query.filter(Condate.start_date == date.today() + timedelta(days=30), Condate.published == True, Condate.cancelled == False).all()
        output = output + "\nCondates happening in a month: \n"
        for c in monthly_notices:
            if indie_tag in c.convention.tags:
                phrase = random.choice(phrases)
                # update phrase num_uses count & remove from pool
                phrase.num_uses += 1
                phrases.remove(phrase)
                message = "%s %s is a month away. %s" % (phrase, c.convention.title, c.convention.url)
                if c.convention.twitter:
                    message = message + " @%s" % (c.convention.twitter)
                output = output + self.post_to_twitter(twitter_api,message) + "\n" + message

        # cons that have registrations closing in a week
        weekly_registration_notices = Condate.query.filter(Condate.registration_closes == date.today() + timedelta(days=7), Condate.published == True, Condate.cancelled == False).all()
        output = output + "\nCondates with registration closing in a week: \n"
        for c in weekly_registration_notices:
            if indie_tag in c.convention.tags:
                phrase = random.choice(phrases)
                # update phrase num_uses count & remove from pool
                phrase.num_uses += 1
                phrases.remove(phrase)
                message = "%s %s registration closes in a week. %s" % (phrase, c.convention.title, c.convention.url)
                if c.convention.twitter:
                    message = message + " @%s" % (c.convention.twitter)
                output = output + self.post_to_twitter(twitter_api,message) + "\n" + message

        # commit updated phrase num_uses counts
        db.session.commit()
        print(output)

manager.add_command('twitter', Twitter())

if __name__ == "__main__":
    manager.run()
