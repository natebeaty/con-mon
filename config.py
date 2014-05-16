import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
HTAUTH_HTPASSWD_PATH = os.path.join(basedir, '.htpasswd')

CSRF_ENABLED = True
SECRET_KEY = 'conconcon-a-gogogo'