import logging,time
from HTMLReport import addImage
from page.boss.boss_login import PageBossLogin
from common.tools import saveCookie

def login_boss(driver,acc_pwd,env,tradingmo=None):
	# 登录boss系统
	driver.get(f'http://0.0.0.0/admin/adminUser/')
	uname,pwd=acc_pwd
	pageBossLogin=PageBossLogin(driver)

	logging.info(f'开始登录,账号 {acc_pwd}')
	pageBossLogin.inputUname(uname)
	pageBossLogin.inputPword(pwd)
	pageBossLogin.clickLogin()
	if pageBossLogin.successFlag(uname):
		logging.info('登录成功')
	else:
		addImage(driver.get_screenshot_as_base64(),'登录失败')

	if tradingmo:
		driver.get(f'http://0.0.0.0/frame/body/load?link_id={tradingmo}')
		time.sleep(10)
		driver.get(f'http://0.0.0.0/tmo-portal/#/pbot-pFund/order')
		time.sleep(3)
		for request in driver.requests:
			if 'existWaitingOrdersFlag' in request.url:
				saveCookie(request.headers['Authorization'],f'pmo_{env}')
				break