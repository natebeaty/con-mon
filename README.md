Con-Mon
=======

![con-mon](https://raw.githubusercontent.com/natebeaty/con-mon/master/static/img/con-mon.png)

Flask app to help frazzled cartoonists keep track of the myriad of conventions in a year.

<https://con-mon.com/>

## Getting up and running

Set up a virtualenv with python 3, e.g.: `pyenv virtualenv 3.7.7 conmon` and then `pip install -r requirements.txt`

Pull down `db/app.db` and set up `config.py`. Run `python app.py` for development server.

For db migrations: `alembic revision -m "add column foo"` and edit migration, then run `alembic upgrade head`

## Flask-Superadmin for Python 3

There are several forks with Python 3 support, this is what I'm doing now:

`pip install https://github.com/closeio/Flask-SuperAdmin/archive/master.zip`
