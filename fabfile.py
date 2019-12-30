from fabric.api import *

env.hosts = ['con-mon.com']
env.user = 'natebeaty'
env.git_branch = 'master'
env.warn_only = True
env.path = '/home/natebeaty/webapps/conmon/conmon'

def deploy():
    update()
    restart()

def install():
    update()
    pip_install()
    restart()

def migrate():
    update()
    alembic_migrate()
    restart()

def update():
    with cd(env.path):
        run('git pull origin %s' % env.git_branch)

def pip_install():
    with cd(env.path):
        run('source .venv/bin/activate && pip install --quiet -r requirements.txt')

def alembic_migrate():
    with cd(env.path):
        run('source .venv/bin/activate && python alembic upgrade head')

def restart():
    with cd(env.path):
        run('../apache2/bin/restart')
