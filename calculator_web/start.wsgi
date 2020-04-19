import os, sys

PROJECT_DIR = '/home/draget/w209'

activate_this = os.path.join(PROJECT_DIR, 'bin', 'activate_this.py')
execfile(activate_this, dict(__file__=activate_this))
sys.path.append(PROJECT_DIR)
#sys.path.append('/home/draget/w209/lib/python3.7')

from w209 import app as application
