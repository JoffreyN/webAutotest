import time,logging,traceback,unittest
from HTMLReport import ddt,addImage,no_retry
from common.parameter import ParameTestCase
from common.apiCenter import addHOld_ttl

from business.login_boss import login_boss
from page.appadmin.structured import PageStructured

from testData.data import structuredPool_test,structuredPool_uat,structuredAcc
from config import bossAcc

# @unittest.skip('跳过')
@ddt.ddt
class TestStructured(ParameTestCase):
	@classmethod
	def setUpClass(cls):
		logging.info(' ########## 结构化交易下单测试开始 ########## ')
		cls.pageStructured=PageStructured(cls.driver)
		login_boss(cls.driver,bossAcc[cls.args.env],cls.args.env)
		cls.driver.get(f"http://{cls.args.env}-****.****.*****/corporate/onboard/list")
		cls.driver.set_window_size(1258,1329)
		
	def setUp(self):
		self.driver.get(f'http://{self.args.env}-****.****.*****/frame/body/load?link_id=524')
		time.sleep(3)
		self.driver.switch_to.frame("boss-frame")

	# @unittest.skip('跳过')
	@no_retry
	# @ddt.data(*structuredPool_test)
	@ddt.data(*structuredPool_uat)
	def test_Structured_01(self,productCode):
		'''结构化交易下单'''
		logging.info(f' ========== 测试开始 Structured-01 结构化交易下单 {productCode} ========== ')
		self.__class__.pageStructured.click_add()
		time.sleep(3)
		self.__class__.pageStructured.input_account(structuredAcc[self.args.env])
		time.sleep(2)
		self.__class__.pageStructured.click_confirm()
		time.sleep(2)
		self.__class__.pageStructured.click_search()
		time.sleep(3)
		self.__class__.pageStructured.input_productCode(productCode)
		self.__class__.pageStructured.click_searchYes()
		time.sleep(3)
		self.__class__.pageStructured.click_result()
		time.sleep(3)
		minimum=self.__class__.pageStructured.get_minimum()
		self.__class__.pageStructured.input_buyAmount(minimum)
		# self.__class__.pageStructured.input_price()
		self.__class__.pageStructured.input_rate1()
		self.__class__.pageStructured.click_checkBox()
		self.__class__.pageStructured.input_recordInfo()
		# self.__class__.pageStructured.input_clarification()
		# self.__class__.pageStructured.input_vcWitness()
		self.__class__.pageStructured.click_submit()
		self.__class__.pageStructured.click_confirm2()
		time.sleep(1)
		if self.__class__.pageStructured.successFlag():
			addImage(self.driver.get_screenshot_as_base64(),f'{productCode} 下单成功')
			self.__class__.pageStructured.click_confirm3()
		else:
			addImage(self.driver.get_screenshot_as_base64(),f'{productCode} 下单失败')
			self.assertTrue(0)

		logging.info(f' ========== 测试结束 Structured-01 结构化交易下单 {productCode} ========== ')

	# @unittest.skip('跳过')
	@no_retry
	# @ddt.data(*structuredPool_test)
	@ddt.data(*structuredPool_uat)
	def test_Structured_02(self,productCode):
		'''结构化交易赎回'''
		logging.info(f' ========== 测试开始 pFund-02 结构化交易赎回 {productCode} ========== ')
		addHOld_ttl(structuredAcc[self.args.env],productCode,'5000','SPMK','D',self.args.env)

		self.__class__.pageStructured.click_add()
		time.sleep(3)
		self.__class__.pageStructured.input_account(structuredAcc[self.args.env])
		time.sleep(2)
		self.__class__.pageStructured.click_confirm()
		time.sleep(2)

		self.__class__.pageStructured.click_redemption()
		self.__class__.pageStructured.click_search(1)
		time.sleep(3)
		self.__class__.pageStructured.input_productCode(productCode)
		self.__class__.pageStructured.click_searchYes()
		time.sleep(3)
		self.__class__.pageStructured.click_result()
		time.sleep(3)
		self.__class__.pageStructured.input_units()
		self.__class__.pageStructured.input_price(n=1)
		# self.__class__.pageStructured.input_rate1(1)
		self.__class__.pageStructured.click_remCheckBox()

		self.__class__.pageStructured.input_remRecordInfo()
		self.__class__.pageStructured.click_remSubmit()
		self.__class__.pageStructured.click_confirm2()

		time.sleep(1)
		if self.__class__.pageStructured.successFlag():
			addImage(self.driver.get_screenshot_as_base64(),f'{productCode} 赎回成功')
			self.__class__.pageStructured.click_confirm3()
		else:
			addImage(self.driver.get_screenshot_as_base64(),f'{productCode} 赎回失败')
			self.assertTrue(0)
		logging.info(f' ========== 测试结束 pFund-02 结构化交易赎回 {productCode} ========== ')

	def tearDown(self):
		pass

	@classmethod
	def tearDownClass(cls):
		logging.info(' ########## 结构化交易下单测试结束 ########## ')

if __name__=='__main__':
	unittest.main()