import logging,time,traceback
from selenium.webdriver.common.by import By
from ..base import PageBase
from common.seleniumError import SCEENVE
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys

class PageStructured(PageBase):
	def __init__(self,driver):
		# 结构化交易下单
		super().__init__(driver)
		self.add=(By.XPATH,"//*[text()='添加订单']")
		self.account=(By.NAME,"accountid")
		self.confirm=(By.XPATH,"//*[text()='确认']")
		self.search=(By.XPATH,"//*[contains(text(),'搜索产品')]")
		self.productCode=(By.XPATH,"//*[@placeholder='输入instrumentID']")
		self.search_yes=(By.XPATH,"//*[text()='搜索']/..")
		self.result=(By.CLASS_NAME,"productCode")
		self.minimum=(By.ID,"subscription-minimum")
		self.buyAmount=(By.NAME,"buyAmount")

		self.price=(By.NAME,"price")
		self.text_rate1=(By.XPATH,"//span[@id='subscription-minimum']/../../../tr[10]/td")
		self.rate1=(By.NAME,"commissionFeeRate")

		# self.text_rate2=(By.XPATH,"//span[@id='subscription-minimum']/../../../tr[12]/td")
		# self.rate2=(By.NAME,"manageFeeRate")
		self.checkBox=(By.CLASS_NAME,"cbr-state")
		self.recordInfo=(By.NAME,"recordInfo")
		self.clarification=(By.NAME,"clarification")
		self.vcWitness=(By.NAME,"vcWitness")
		self.staffName=(By.NAME,"staffName")

		self.submit=(By.CLASS_NAME,"subscription-btn-save")
		self.confirm2=(By.XPATH,"//*[@id='modal-confirm']//button[text()='确定']")
		self.flag=(By.XPATH,"//p[contains(text(),'提交订单成功')]")
		self.confirm3=(By.XPATH,"//*[@id='modal-alert']//button[text()='确定']")

		self.redemption=(By.ID,"redemption")
		self.units=(By.NAME,"units")

		self.rem_checkBox=(By.XPATH,"//form[@id='redemption-box']//div[@class='cbr-state']")
		self.rem_recordInfo=(By.XPATH,"//form[@id='redemption-box']//input[@name='recordInfo']")
		self.rem_submit=(By.CLASS_NAME,"redemption-btn-save")

		self.custRatioRisk=(By.NAME,'custRatioRisk')
		self.middleSuggest=(By.NAME,'middleSuggest')
		self.productMayRisk=(By.NAME,'productMayRisk')

	def input_productMayRisk(self):
		logging.info(f'输入产品可能面对的下行风险')
		self.findElement(self.productMayRisk).send_keys('产品可能面对的下行风险 from webAutoTest')

	def input_middleSuggest(self):
		logging.info(f'输入中介人建议原因')
		self.findElement(self.middleSuggest).send_keys('中介人建议原因 from webAutoTest')

	def select_custRatioRisk(self):
		logging.info(f'选择客户集中风险')
		Select(self.findElement(self.custRatioRisk)).select_by_value("1")

	def click_remSubmit(self):
		logging.info(f'点击提交赎回订单')
		self.findElement(self.rem_submit).click()

	def input_remRecordInfo(self):
		logging.info(f'输入赎回recordInfo')
		self.findElement(self.rem_recordInfo).send_keys('rem recordInfo from webAutoTest')

	def click_remCheckBox(self):
		logging.info(f'点击勾选沽售指示')
		self.findElement(self.rem_checkBox).click()

	def input_units(self,units='200'):
		logging.info(f'输入赎回份额: {units}')
		self.findElement(self.units).send_keys(units)

	def click_redemption(self):
		logging.info(f'点击 赎回tab')
		self.findElement(self.redemption).click()


	def click_add(self):
		logging.info(f'点击添加订单')
		self.findElement(self.add).click()

	def input_account(self,account):
		logging.info(f'输入账户号: {account}')
		ele=self.findElement(self.account)
		ele.send_keys(account)
		ele.send_keys(Keys.ENTER)

	def click_confirm(self):
		logging.info(f'点击确认')
		self.findElement(self.confirm).click()

	def click_search(self,n=0):
		logging.info(f'点击 搜索产品')
		self.findElements(self.search,until='located')[n].click()

	def input_productCode(self,productCode):
		logging.info(f'输入产品id: {productCode}')
		self.findElement(self.productCode).send_keys(productCode)

	def click_searchYes(self):
		logging.info(f'点击 搜索')
		self.findElement(self.search_yes).click()

	def click_result(self):
		logging.info(f'点击 搜索结果的第一条')
		self.findElement(self.result).click()

	def get_minimum(self):
		minimum=self.findElement(self.minimum).text
		logging.info(f'获取最小申购金额 {minimum}')
		return minimum

	def input_buyAmount(self,amount='100000'):
		try:
			amount=max(float(amount),100000)
		except:
			amount=100000
		logging.info(f'输入最小认购金额: {amount}')
		self.findElement(self.buyAmount).send_keys(str(amount))

	def input_price(self,price='69.8',n=0):
		logging.info(f'输入order price: {price}')
		self.findElements(self.price,until='located')[n].send_keys(price)

	def input_rate1(self,n=0):
		# try:
		# 	rate=self.findElement(self.text_rate1).text.strip()[:-1]
		# except:
		rate='1.5'
		logging.info(f'输入rate1: {rate}')
		self.findElements(self.rate1,until='located')[n].send_keys(rate)

	# def input_rate2(self):
	# 	rate=self.findElement(self.text_rate2).text.strip()[:-1]
	# 	logging.info(f'输入rate2: {rate}')
	# 	self.findElement(self.rate2).send_keys(rate)

	def click_checkBox(self):
		logging.info(f'点击 勾选同意')
		for ele in self.findElements(self.checkBox,until='located'):
			try:
				self.driver.execute_script("arguments[0].click();",ele)
			except:
				traceback.print_exc()

	def input_clarification(self):
		logging.info(f'输入澄清')
		self.findElement(self.clarification).send_keys('clarification from webAutoTest')

	def input_vcWitness(self):
		logging.info(f'输入 vcWitness')
		self.findElement(self.vcWitness).send_keys('vcWitness from webAutoTest')

	def click_submit(self):
		logging.info(f'点击 提交')
		self.findElement(self.submit).click()

	def click_confirm2(self):
		logging.info(f'点击 确定2')
		try:
			self.findElement(self.confirm2).click()
		except:
			pass

	def successFlag(self):
		return self.isEleExists(self.flag,timeout=5)

	def click_confirm3(self):
		logging.info(f'点击 确定3')
		self.findElement(self.confirm3).click()
