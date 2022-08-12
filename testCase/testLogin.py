import time,logging,traceback,unittest
from common.parameter import ParameTestCase
from business.login_out import logout

from page.login_all import PageLogin
from page.header_bar import PageHeaderBar
from page.alert import PageAlert

from testData.data import accountPool,accBinding

# @unittest.skip('跳过')
# @ddt.ddt
class TestLogin(ParameTestCase):
	@classmethod
	def setUpClass(cls):
		logging.info(' ########## 登录测试开始 ########## ')
		cls.pageLogin=PageLogin(cls.driver)
		cls.pageHeaderBar=PageHeaderBar(cls.driver)
		cls.pageAlert=PageAlert(cls.driver)

	def setUp(self):
		logout(self.driver)

	# @no_retry
	# @unittest.skip('跳过')
	def test_CMBI_01(self):
		'''手机号+密码 登录'''
		logging.info(f' ========== 测试开始 CMBI-01 手机号+密码 登录 ========== ')
		phone=accBinding[self.args.account][1]
		pwd=accountPool[phone]
		self.__class__.pageLogin.inputUname(phone)
		self.__class__.pageLogin.clickLogin()
		self.__class__.pageLogin.inputPword(pwd)
		self.__class__.pageLogin.clickLogin('确认')
		self.assertIsNone(self.__class__.pageAlert.getAntMsg())
		time.sleep(2)
		self.assertNotIn('login',self.driver.current_url)
		logging.info(f'{phone} {pwd} 登录完成')

		logging.info(f' ========== 测试结束 CMBI-01 手机号+密码 登录 ========== ')


	# @no_retry
	# @unittest.skip('跳过')
	def test_CMBI_02(self):
		'''现金账户+密码 登录'''
		logging.info(f' ========== 测试开始 CMBI-02 现金账户+密码 登录 ========== ')
		pwd=accountPool[self.args.account]

		self.__class__.pageLogin.inputUname(self.args.account)
		self.__class__.pageLogin.clickLogin()
		self.__class__.pageLogin.inputPword(pwd)
		self.__class__.pageLogin.clickLogin('确认')
		self.assertIsNone(self.__class__.pageAlert.getAntMsg())

		if self.__class__.pageLogin.smsFlag():
			logging.info('要求输入验证码')
			self.__class__.pageLogin.clickSMS()
			self.__class__.pageLogin.clickLogin('确认')
			# from testData.data import accBinding
			# phone=accBinding[acc_pwd[0]][1]
			# code=getSMScode(phone,args.env,6)
			self.__class__.pageLogin.inputSMS('888888')
			self.__class__.pageLogin.clickLogin('确认')
		else:
			logging.info('未要求输入验证码')
		time.sleep(2)
		self.__class__.pageLogin.clickLogin('我知道了')
		time.sleep(2)
		self.assertNotIn('login',self.driver.current_url)
		logging.info(f'{self.args.account} {pwd} 登录完成')

		logging.info(f' ========== 测试结束 CMBI-02 现金账户+密码 登录 ========== ')


	def tearDown(self):
		pass

	@classmethod
	def tearDownClass(cls):
		logging.info(' ########## 登录测试结束 ########## ')

if __name__=='__main__':
	unittest.main()