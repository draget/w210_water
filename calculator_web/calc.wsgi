import os, sys

PROJECT_DIR = '/opt/w210/w210_water/calculator_web/'

#activate_this = os.path.join(PROJECT_DIR, 'bin', 'activate_this.py')
#execfile(activate_this, dict(__file__=activate_this))
sys.path.append(PROJECT_DIR)
#sys.path.append('/home/draget/w209/lib/python3.7')

from calc import server as application
