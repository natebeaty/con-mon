from fabric import task
from invoke import run as local

remote_path = "/home/natebeaty/apps/con-mon/conmon"
remote_hosts = ["natebeaty@con-mon.com"]
git_branch = "master"

# deploy
@task(hosts=remote_hosts)
def deploy(c):
    update(c)
    restart(c)

# install
@task(hosts=remote_hosts)
def install(c):
    update(c)
    pip_install(c)
    restart(c)

# migrate
@task(hosts=remote_hosts)
def migrate(c):
    update(c)
    alembic_migrate(c)
    restart(c)

def update(c):
    print("Pulling new code...")
    c.run("cd {} && git pull origin {}".format(remote_path, git_branch))

def alembic_migrate(c):
    print("Running db migrations...")
    c.run("cd {} && source .venv/bin/activate && python alembic upgrade head".format(remote_path))

def restart(c):
    print("Restarting app...")
    c.run("cd {} && ../stop && ../start".format(remote_path))

# local commands
@task
def dev(c):
    local("python app.py")
