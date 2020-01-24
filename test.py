import subprocess
import os
import time
while True:	
	x = subprocess.check_output(['bash','runner.sh'])
	if 'fail' in x.decode("UTF-8"):
		break



