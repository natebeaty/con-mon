#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':
    main(url='sqlite:///app.db', debug='False', six='<module \'six\' from \'/Users/natebeaty/.virtualenvs/con-mon/lib/python2.7/site-packages/six.pyc\'>', repository='db_repository')
