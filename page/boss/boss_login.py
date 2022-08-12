import logging,time
from selenium.webdriver.common.by import By
from ..base import PageBase

class PageBossLogin(PageBase):
	def __init__(self,driver):
		# boss 登录相关页面
		super().__init__(driver)
		self.input_uname=(By.ID,'account')
		self.input_pword=(By.ID,'passwd')
		self.btn_login=(By.ID,'login_console')

	def inputUname(self,uname):
		logging.info(f'输入用户名 {uname}')
		self.findElement(self.input_uname).send_keys(uname)

	def inputPword(self,pword):
		logging.info(f'输入密码 {pword}')
		self.findElement(self.input_pword).send_keys(pword)

	def clickLogin(self):
		logging.info(f'点击 登录')
		self.findElement(self.btn_login).click()
		time.sleep(2)

	def successFlag(self,uname):
		_flagXPATH=(By.XPATH,f'//*[contains(text(),"{uname}") or contains(text(),"{uname.upper()}") or contains(text(),"{uname.lower()}")]')
		return self.isEleExists(_flagXPATH,timeout=3)
