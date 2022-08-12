import logging,time
from selenium.webdriver.common.by import By
from .base import PageBase

class PageLogin(PageBase):
	def __init__(self,driver):
		# 登录相关页面
		super().__init__(driver)
		self.input_uname=(By.XPATH,'//div[@class="input-box"]/input[1]')
		self.btn_login=(By.CLASS_NAME,'btn-login')
		self.input_pword=(By.XPATH,'//div[@class="input-box"]/input[@type="password"]')

		self.forget_uname=(By.XPATH,'//div[@class="tips-btn"]/span[1]')

		self.btn_SMS=(By.XPATH,"//div[contains(text(),'手机短信认证')]")
		self.input_sms=(By.XPATH,'//div[@class="input-box"]/input[@placeholder="请输入验证码"]')
		# self.btn_iknow=(By.XPATH,"//button[contains(text(),'我知道了')]")

	def inputUname(self,uname):
		logging.info(f'输入用户名 {uname}')
		self.findElement(self.input_uname).send_keys(uname)

	def clickLogin(self,msg='注册/登录'):
		logging.info(f'点击 {msg}')
		self.findElement(self.btn_login).click()

	def inputPword(self,pword):
		logging.info(f'输入密码 {pword}')
		self.findElement(self.input_pword).send_keys(pword)

	def clickForgetUname(self):
		logging.info(f'点击 忘记密码')
		self.findElement(self.forget_uname).click()

	def smsFlag(self):
		return self.isEleExists(self.btn_SMS,timeout=3)

	def clickSMS(self):
		logging.info(f'点击 手机短信认证')
		self.findElement(self.btn_SMS).click()

	def inputSMS(self,smscode):
		logging.info(f'输入验证码 {smscode}')
		self.findElement(self.input_sms).send_keys(smscode)


















