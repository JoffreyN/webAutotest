import logging,time
from selenium.webdriver.common.by import By
from .base import PageBase

class PageFooter(PageBase):
	def __init__(self,driver):
		# 页面最底部
		super().__init__(driver)
		self.version=(By.CLASS_NAME,'edition')



	def getVersion(self):
		logging.info(f'获取版本号')
		versionInfo=self.findElement(self.version).text
		return versionInfo.split('：')[1]

