from flask import Flask
from flask.ext.script import Manager,Command
from datetime import date, datetime, timedelta
from app import Condate
import config
import twitter
import random

app = Flask(__name__)
manager = Manager(app)

class Twitter(Command):
    """
    Twitter alerts! 
    Weekly and monthly notices of oncoming conventions
    Weekly notices of oncoming deadlines
    """

    def post_to_twitter(self,twitter_api,message):
        try:
            twitter_api.PostUpdate(message)
            return ''
        except:
            return "There was an error posting '%s' to twitter. Please write Nate and mock him." % message

    def run(self):
        phrases = (
            'Heads up!',
            'Cartoonists!',
            'Drop that pencil!',
            'Take note!',
            'Hey-o!',
            'Whoa!',
            'OMG',
            'Just a friendly reminder:',
            'Did you know?',
            'Very important:',
            'Nerd PSA:',
            'Don\'t freak out!',
            'Keep calm:',
            'Mark your calendar!',
        )
        twitter_api = twitter.Api(consumer_key=config.TWITTER_CONSUMER_KEY, consumer_secret=config.TWITTER_CONSUMER_SECRET, access_token_key=config.TWITTER_ACCESS_TOKEN_KEY, access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET)

        # cons that are a week away
        daily_notices = Condate.query.filter(Condate.start_date == date.today() + timedelta(days=7)).all()
        output = "Condates happening in a week: \n"
        for c in daily_notices:
            message = "%s %s is a week away! %s" % (random.choice(phrases), c.convention.title, c.convention.url)
            output = output + self.post_to_twitter(twitter_api,message) + "\n" + message

        # cons that are a month away
        monthly_notices = Condate.query.filter(Condate.start_date == date.today() + timedelta(days=30)).all()
        output = output + "\nCondates happening in a month: \n"
        for c in monthly_notices:
            message = "%s %s is a month away! %s" % (random.choice(phrases), c.convention.title, c.convention.url)
            output = output + self.post_to_twitter(twitter_api,message) + "\n" + message

        # cons that have registrations closing in a week
        weekly_registration_notices = Condate.query.filter(Condate.registration_closes == date.today() + timedelta(days=7)).all()
        output = output + "\nCondates with registration closing in a week: \n"
        for c in weekly_registration_notices:
            message = "%s %s registration closes in a week! %s" % (random.choice(phrases), c.convention.title, c.convention.url)
            output = output + self.post_to_twitter(twitter_api,message) + "\n" + message

        print output

manager.add_command('twitter', Twitter())

if __name__ == "__main__":
    manager.run()
