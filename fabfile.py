from fabric.api import *

env.project_name = 'con-mon'
env.hosts = ['cons.clixel.com']
env.user = 'natebeaty'
env.git_branch = 'master'
env.warn_only = True
env.path = '/var/www/%s/public_html' % (env.project_name)

def deploy():
    update()
    pip_install()
    restart()

def update():
    with cd(env.path):
        run('git pull origin %s' % env.git_branch)

def pip_install():
    with cd(env.path):
        run('pip install -r requirements.txt')

def restart():
    with cd(env.path):
        sudo('/etc/init.d/uwsgi restart')
