Con-Mon
=======

![con-mon](https://raw.githubusercontent.com/natebeaty/con-mon/master/static/img/con-mon.png)

Flask app to help frazzled cartoonists keep track of the myriad of conventions in a year.

<https://con-mon.com/>

## Getting up and running

Set up a virtualenv with python 3, and `pip install -r requirements.txt`

Pull down `db/app.db` and set up `config.py`. Run `python app.py` for development server.

For db migrations: `alembic revision -m "add column foo"` and edit migration, then run `alembic upgrade head`
