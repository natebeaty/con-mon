#!/usr/bin/env python

import os
import readline
from pprint import pprint

from flask import *

from app import *
from cronjobs import *

os.environ['PYTHONINSPECT'] = 'True'
