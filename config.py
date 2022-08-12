bossAcc={
	'test':['admin03','******'],
	'uat':['uatAdmin','******']
}

import sys,os
platform=sys.platform
if platform=='darwin':
	ip=[a for a in os.popen('ifconfig en2').readlines() if 'inet' in a][1].split()[1]
	port='80'
	host=f'http://{ip}:{port}/report'
	genPath=os.path.join(sys.path[0],'report/')
	webPath='~/zp/www/report/'
elif platform=='win32':
	# ip=[a for a in os.popen('route print').readlines() if ' 0.0.0.0 ' in a][0].split()[-2]
	ip='10.0.2.51'
	port='80'
	host=f'http://{ip}:{port}/report'
	genPath=os.path.join(sys.path[0],'report/')
	webPath='~/WWW/report'
