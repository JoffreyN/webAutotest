import logging,time
from HTMLReport import addImage
from page.login_all import PageLogin
from page.header_bar import PageHeaderBar
from page.alert import PageAlert


def login(driver,acc_pwd,forceLogout=0,args=None,acc=1):
	# forceLogout 0表示登录前先检测是否已登陆，是则直接返回；1表示如果已登录，则先退出，再登录
	# acc=0 只登陆手机号 不登录账户
	uname,pwd=acc_pwd
	pageLogin=PageLogin(driver)
	pageHeaderBar=PageHeaderBar(driver)
	pageAlert=PageAlert(driver)
	for i in range(5):
		driver.refresh()
		if 'login' in driver.current_url:
			pass
		else:
			acc_code=pageHeaderBar.getAcc_code()
			if acc_code==uname:# 已是登录状态
				if forceLogout:#需要强制登出
					logging.info('检测到已登录指定的账号，强制先登出……')
					logout(driver)
				else:#不需要强制登出
					logging.info('检测到已登录指定的账号，无需登录……')
					return
			else:
				logging.info('检测到已登录其它账号，需先登出……')
				logout(driver)
		logging.info(f'开始登录,账号 {acc_pwd}')
		pageLogin.inputUname(uname)
		pageLogin.clickLogin()
		pageLogin.inputPword(pwd)
		pageLogin.clickLogin('确认')
		antMsg=pageAlert.getAntMsg()
		if antMsg:raise Exception(f'登录失败: {antMsg}')

		if acc:
			if pageLogin.smsFlag():
				logging.info('要求输入验证码')
				pageLogin.clickSMS()
				pageLogin.clickLogin('确认')
				# from testData.data import accBinding
				# phone=accBinding[acc_pwd[0]][1]
				# code=getSMScode(phone,args.env,6)
				pageLogin.inputSMS('888888')
				pageLogin.clickLogin('确认')
			else:
				logging.info('未要求输入验证码')
			pageLogin.clickLogin('我知道了')
			time.sleep(2)
			if 'login' in driver.current_url:
				time.sleep(1);continue
			else:break
	logging.info(f'{uname} {pwd} 登录完成')


def logout(driver):
	driver.refresh()
	if 'login' in driver.current_url:
		logging.info('已是登出状态')
	else:
		pageHeaderBar=PageHeaderBar(driver)
		pageHeaderBar.clickUserinfo()
		pageHeaderBar.clickLogout()

