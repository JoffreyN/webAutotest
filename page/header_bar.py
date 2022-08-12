import logging,time
from selenium.webdriver.common.by import By
from .base import PageBase

class PageHeaderBar(PageBase):
	def __init__(self,driver):
		# 页面顶部头 和 页面左侧导航栏
		super().__init__(driver)
		self.acc_code=(By.CLASS_NAME,'account-num')
		self.acc_type=(By.XPATH,'//div[@class="account-box"]/span[1]')
		self.input_search=(By.CLASS_NAME,'stockSearchInput')
		self.searceResult=(By.XPATH,'//*[@class="stockSearch"]//*[@class="drop-down-in-box"]//li')
		self.btn_userInfo=(By.CLASS_NAME,'header-user')
		self.btn_logout=(By.XPATH,"//div[contains(text(),'用户登出')]")
		

		self.side_Market=(By.XPATH,'//li[@data-menu-id="Market"]')# 市场
		self.side_Stocks=(By.XPATH,'//li[@data-menu-id="Stocks"]')# 自选
		self.side_Trade=(By.XPATH,'//li[@data-menu-id="Trade"]')# 交易
		self.side_assetView=(By.XPATH,'//li[@data-menu-id="assetView"]')# 账户
		self.side_Information=(By.XPATH,'//li[@data-menu-id="Information"]')# 资讯
		self.side_More=(By.XPATH,'//li[@data-menu-id="More"]')# 更多

		self.btn_setting=(By.CLASS_NAME,'menu-setting-img')

	def input_keyword(self,keyword):
		logging.info(f'输入关键词 {keyword}')
		ele=self.findElement(self.input_search)
		ele.clear()
		ele.send_keys(keyword)

	def click_resultOne(self):
		logging.info(f'点击 第一条搜索结果')
		self.findElements(self.searceResult)[0].click()

	def getAcc_code(self):
		logging.info(f'获取账户号码')
		return self.findElement(self.acc_code).text.strip()
		
	def getAcc_type(self):
		logging.info(f'获取账户类型')
		return self.findElement(self.acc_type).text.strip()

	def clickUserinfo(self):
		logging.info(f'点击 弹出用户信息')
		self.findElement(self.btn_userInfo).click()
	
	def clickLogout(self):
		logging.info(f'点击 用户登出')
		self.findElement(self.btn_logout).click()

	def clickMarket(self):
		logging.info(f'点击 市场')
		self.findElement(self.side_Market).click()

	def clickStocks(self):
		logging.info(f'点击 自选')
		self.findElement(self.side_Stocks).click()

	def clickTrade(self):
		logging.info(f'点击 交易')
		self.findElement(self.side_Trade).click()

	def clickassetView(self):
		logging.info(f'点击 账户')
		self.findElement(self.side_assetView).click()

	def clickInformation(self):
		logging.info(f'点击 资讯')
		self.findElement(self.side_Information).click()

	def clickMore(self):
		logging.info(f'点击 更多')
		self.findElement(self.side_More).click()

	def clickSetting(self):
		logging.info(f'点击 手机短信认证')
		self.findElement(self.btn_setting).click()





