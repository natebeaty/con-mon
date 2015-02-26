from flask import Flask
from flask.ext.script import Manager,Command
from datetime import date, datetime, timedelta
from app import Condate,Tag
import config
import twitter
import random

app = Flask(__name__)
manager = Manager(app)

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
        phrases = (
            'Heads up!',
            'Cartoonists!',
            'Hey doodlers!',
            'Drop that pencil!',
            'Take note!',
            'Hey-o!',
            'What what what:',
            'I just thought of something:',
            'It\'s official:',
            'I feel a tingling in the force:',
            'Just when you thought you were safe:',
            'Yo cuz:',
            'Boys and girls:',
            'Drop that Wacom!',
            'Get stapling!',
            'Fire up the Risograph!',
            'Slather in on the offset!',
            'Get your butt scanning!',
            'Bust out the bristol!',
            'Refill that pocketbrush!',
            'Replace that frazzled Micron:',
            'Dip that nib!',
            'Drop that ruler!',
            'Put down the fountain pen!',
            'Finish that masterpiece!',
            'Uh-oh:',
            'Hey, uh:',
            'Look, buddy:',
            'Get excited:',
            'I have something very important to tell you:',
            'Shhhhhhh:',
            'Hey! You! Yeah you!',
            'My robot brain informed me that',
            'My robot brain informed me that',
            'I just heard that',
            'Whoa!',
            'OMG',
            'Just a friendly reminder:',
            'Did you know?',
            'Very important:',
            'Nerd PSA:',
            'Don\'t freak out!',
            'Keep it together:',
            'Mark your calendar!',
        )
        twitter_api = twitter.Api(consumer_key=config.TWITTER_CONSUMER_KEY, consumer_secret=config.TWITTER_CONSUMER_SECRET, access_token_key=config.TWITTER_ACCESS_TOKEN_KEY, access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET)
        superhero_tag = Tag.query.filter(Tag.title == "Superhero").first()

        # cons that are a week away
        daily_notices = Condate.query.filter(Condate.start_date == date.today() + timedelta(days=7), Condate.published == True).all()
        output = "Condates happening in a week: \n"
        for c in daily_notices:
            if superhero_tag not in c.convention.tags:
                message = "%s %s is a week away. %s" % (random.choice(phrases), c.convention.title, c.convention.url)
                if c.convention.twitter:
                    message = message + " @%s" % (c.convention.twitter)
                output = output + self.post_to_twitter(twitter_api,message) + "\n" + message

        # cons that are a month away
        monthly_notices = Condate.query.filter(Condate.start_date == date.today() + timedelta(days=30), Condate.published == True).all()
        output = output + "\nCondates happening in a month: \n"
        for c in monthly_notices:
            if superhero_tag not in c.convention.tags:
                message = "%s %s is a month away. %s" % (random.choice(phrases), c.convention.title, c.convention.url)
                if c.convention.twitter:
                    message = message + " @%s" % (c.convention.twitter)
                output = output + self.post_to_twitter(twitter_api,message) + "\n" + message

        # cons that have registrations closing in a week
        weekly_registration_notices = Condate.query.filter(Condate.registration_closes == date.today() + timedelta(days=7), Condate.published == True).all()
        output = output + "\nCondates with registration closing in a week: \n"
        for c in weekly_registration_notices:
            if superhero_tag not in c.convention.tags:
                message = "%s %s registration closes in a week. %s" % (random.choice(phrases), c.convention.title, c.convention.url)
                if c.convention.twitter:
                    message = message + " @%s" % (c.convention.twitter)
                output = output + self.post_to_twitter(twitter_api,message) + "\n" + message

        print output

manager.add_command('twitter', Twitter())

if __name__ == "__main__":
    manager.run()
