import logging,time,traceback
from selenium.webdriver.common.by import By
from ..base import PageBase
from common.seleniumError import SCEENVE
from selenium.webdriver.support.select import Select

class PageBond(PageBase):
	def __init__(self,driver):
		# 交易中台
		super().__init__(driver)
		# http://tradingmo-uat.cmbi.online/tmo-portal/#/pbot-pFund/order
		self.prdCode=(By.XPATH,"//label[contains(text(),'产品代码')]/..//input")
		self.queryBtn=(By.XPATH,"//label[contains(text(),'产品代码')]/../following-sibling::li[2]/button[1]")#查询按钮




	# 	self.account=(By.NAME,"accountid")
	# 	self.confirm=(By.XPATH,"//*[text()='确认']")
	# 	self.search=(By.XPATH,"//*[contains(text(),'搜索产品')]")
	# 	self.productCode=(By.XPATH,"//*[@placeholder='输入instrumentID']")
	# 	self.search_yes=(By.XPATH,"//*[text()='搜索']/..")
	# 	self.result=(By.CLASS_NAME,"productCode")
	# 	self.minimum=(By.ID,"subscription-minimum")
	# 	self.buyAmount=(By.NAME,"buyAmount")

	# 	self.price=(By.NAME,"price")
	# 	self.text_rate1=(By.XPATH,"//span[@id='subscription-minimum']/../../../tr[10]/td")
	# 	self.rate1=(By.NAME,"commissionFeeRate")

	# 	# self.text_rate2=(By.XPATH,"//span[@id='subscription-minimum']/../../../tr[12]/td")
	# 	# self.rate2=(By.NAME,"manageFeeRate")
	# 	self.checkBox=(By.CLASS_NAME,"cbr-state")
	# 	self.recordInfo=(By.NAME,"recordInfo")
	# 	self.clarification=(By.NAME,"clarification")
	# 	self.vcWitness=(By.NAME,"vcWitness")

	# 	self.submit=(By.CLASS_NAME,"subscription-btn-save")
	# 	self.confirm2=(By.XPATH,"//*[@id='modal-confirm']//button[text()='确定']")
	# 	self.flag=(By.XPATH,"//p[contains(text(),'提交订单成功')]")
	# 	self.confirm3=(By.XPATH,"//*[@id='modal-alert']//button[text()='确定']")

	# 	self.redemption=(By.ID,"redemption")
	# 	self.units=(By.NAME,"units")

	# 	self.rem_checkBox=(By.XPATH,'//*[@name="agreeSellDda"]/../..')
	# 	self.rem_recordInfo=(By.XPATH,"//form[@id='redemption-box']//input[@name='commissionFeeRate']/../../following-sibling::tr[5]//input[1]")
	# 	self.rem_submit=(By.CLASS_NAME,"redemption-btn-save")

	# 	self.custRatioRisk=(By.NAME,'custRatioRisk')
	# 	self.middleSuggest=(By.NAME,'middleSuggest')
	# 	self.productMayRisk=(By.NAME,'productMayRisk')

	# def input_productMayRisk(self):
	# 	logging.info(f'输入产品可能面对的下行风险')
	# 	self.findElement(self.productMayRisk).send_keys('产品可能面对的下行风险 from webAutoTest')

	# def input_middleSuggest(self):
	# 	logging.info(f'输入中介人建议原因')
	# 	self.findElement(self.middleSuggest).send_keys('中介人建议原因 from webAutoTest')
