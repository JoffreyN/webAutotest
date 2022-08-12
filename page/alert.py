import logging,time
from selenium.webdriver.common.by import By
from .base import PageBase

class PageAlert(PageBase):
	def __init__(self,driver):
		# 弹窗 或 提示
		super().__init__(driver)
		self.antMsg=(By.CLASS_NAME,'ant-message')
		

	def getAntMsg(self):
		try:
			return self.findElement(self.antMsg,screen=False,timeout=3,until='located').text.strip()
		except AttributeError:
			return None

