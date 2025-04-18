from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Command
from datetime import date, datetime, timedelta
from app import Condate, Tag, Phrase
import config
import random
# from mastodon import Mastodon
from atproto import Client, client_utils

app = Flask(__name__)
app.config.from_object('config')
manager = Manager(app)
db = SQLAlchemy(app)

class Social(Command):
    """
    Social alerts!
    Weekly and monthly notices of approaching convention dates
    Weekly notices of approaching registration deadlines
    """

    # def post_to_mastodon(self, mastodon_api, message):
    #     try:
    #         mastodon_api.toot(message)
    #         return ''
    #     except:
    #         return "There was an error posting to Mastodon.\n"

    def post_to_bluesky(self, bluesky_api, message):
        try:
            bluesky_api.send_post(message)
            return ''
        except:
            return "There was an error posting to Bluesky.\n"

    def run(self):
        # mastodon_api = Mastodon(access_token=config.MASTODON_ACCESS_TOKEN, api_base_url=config.MASTODON_BASE_URL)
        bluesky_api = Client()
        bluesky_api.login(config.BLUESKY_USERNAME, config.BLUESKY_PASSWORD)

        # get indie_tag for filtering
        indie_tag = Tag.query.filter(Tag.title == "Indie").first()

        # get least used phrases pool
        min_uses = db.session.query(db.func.min(Phrase.num_uses)).scalar()
        phrases = Phrase.query.filter(Phrase.num_uses == min_uses).all()

        output = "-----------------\nSocial cronjob: %s\n\n" % str(datetime.now())

        # cons that are a week away
        daily_notices = Condate.query.filter(Condate.start_date == date.today() + timedelta(days=7), Condate.published == True, Condate.cancelled == False).all()
        output = output + "Condates happening in a week: \n"
        for c in daily_notices:
            if indie_tag in c.convention.tags:
                phrase = random.choice(phrases)
                # update phrase num_uses count & remove from pool
                phrase.num_uses += 1
                phrases.remove(phrase)
                message = "%s %s is a week away. %s" % (phrase, c.convention.title, c.convention.url)
                # output = output + self.post_to_mastodon(mastodon_api, message)
                bluesky_message = client_utils.TextBuilder().text("%s " % phrase).link(c.convention.title, c.convention.url).text(" is a week away.");
                output = output + self.post_to_bluesky(bluesky_api, bluesky_message)
                output = output + "\n" + message

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
                # output = output + self.post_to_mastodon(mastodon_api, message)
                bluesky_message = client_utils.TextBuilder().text("%s " % phrase).link(c.convention.title, c.convention.url).text(" is a month away.");
                output = output + self.post_to_bluesky(bluesky_api, bluesky_message)
                output = output + "\n" + message

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
                # output = output + self.post_to_mastodon(mastodon_api, message)
                bluesky_message = client_utils.TextBuilder().text("%s " % phrase).link(c.convention.title, c.convention.url).text(" registration closes in a week.");
                output = output + self.post_to_bluesky(bluesky_api, bluesky_message)
                output = output + "\n" + message

        # commit updated phrase num_uses counts
        db.session.commit()
        print(output)

manager.add_command('social', Social())

if __name__ == "__main__":
    manager.run()
