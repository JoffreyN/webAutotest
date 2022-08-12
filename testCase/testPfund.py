import time,logging,traceback,unittest
from HTMLReport import ddt,addImage,no_retry
from common.parameter import ParameTestCase
from common.apiCenter import addHOld_ttl

from business.login_boss import login_boss
from page.appadmin.pFund import PagePfund

from testData.data import fundPool_test,fundPool_uat,fundAcc
from config import bossAcc

# @unittest.skip('跳过')
@ddt.ddt
class TestPfund(ParameTestCase):
	@classmethod
	def setUpClass(cls):
		logging.info(' ########## 私募基金下单测试开始 ########## ')
		cls.pagePfund=PagePfund(cls.driver)
		login_boss(cls.driver,bossAcc[cls.args.env],cls.args.env,'appadmin')
		cls.driver.set_window_size(1258,1329)
		
	def setUp(self):
		self.driver.get(f'http://{self.args.env}-*****.****.******/admin/pFundOrder/list')
		time.sleep(3)

	# @unittest.skip('跳过')
	@no_retry
	# @ddt.data(*fundPool_test)
	@ddt.data(*fundPool_uat)
	def test_pFund_01(self,productCode):
		'''私募基金下单'''
		logging.info(f' ========== 测试开始 pFund-01 私募基金下单 {productCode} ========== ')
		self.__class__.pagePfund.click_add()
		time.sleep(3)
		self.__class__.pagePfund.input_account(fundAcc[self.args.env])
		time.sleep(2)
		self.__class__.pagePfund.click_confirm()
		time.sleep(2)
		self.__class__.pagePfund.click_search()
		time.sleep(3)
		self.__class__.pagePfund.input_productCode(productCode)
		self.__class__.pagePfund.click_searchYes()
		time.sleep(3)
		self.__class__.pagePfund.click_result()
		time.sleep(3)
		self.__class__.pagePfund.input_recordInfo()
		self.__class__.pagePfund.input_clarification()
		minimum=self.__class__.pagePfund.get_minimum()
		power=getPower(bondAcc[self.args.env],productCode,types='pFundOrder',env=self.args.env)
		logging.info(f'下单前购买力: {power}')
		self.__class__.pagePfund.input_buyAmount(minimum)
		self.__class__.pagePfund.input_rate1()
		self.__class__.pagePfund.input_rate2()
		self.__class__.pagePfund.click_checkBox()
		self.__class__.pagePfund.click_submit()
		self.__class__.pagePfund.click_confirm2()
		time.sleep(1)
		if self.__class__.pagePfund.successFlag():
			addImage(self.driver.get_screenshot_as_base64(),f'{productCode} 下单成功')
			self.__class__.pagePfund.click_confirm3()
			power2=getPower(bondAcc[self.args.env],productCode,types='pFundOrder',env=self.args.env)
			logging.info(f'下单后购买力: {power2}')
			self.assertNotEqual(power,power2)
		else:
			addImage(self.driver.get_screenshot_as_base64(),f'{productCode} 下单失败')
			self.assertTrue(0)

		logging.info(f' ========== 测试结束 pFund-01 私募基金下单 {productCode} ========== ')

	# @unittest.skip('跳过')
	@no_retry
	# @ddt.data(*fundPool_test)
	@ddt.data(*fundPool_uat)
	def test_pFund_02(self,productCode):
		'''私募基金赎回'''
		logging.info(f' ========== 测试开始 pFund-02 私募基金赎回 {productCode} ========== ')
		addHOld_ttl(fundAcc[self.args.env],productCode,'5000','FUND','D',self.args.env)
		self.__class__.pagePfund.click_add()
		time.sleep(3)
		self.__class__.pagePfund.input_account(fundAcc[self.args.env])
		time.sleep(2)
		self.__class__.pagePfund.click_confirm()
		time.sleep(2)

		self.__class__.pagePfund.click_redemption()
		self.__class__.pagePfund.click_search(1)
		time.sleep(3)
		self.__class__.pagePfund.input_productCode(productCode)
		self.__class__.pagePfund.click_searchYes()
		time.sleep(3)
		self.__class__.pagePfund.click_result()
		time.sleep(3)
		self.__class__.pagePfund.input_units()
		self.__class__.pagePfund.input_redemptionFeeRate()
		self.__class__.pagePfund.click_remCheckBox()
		self.__class__.pagePfund.input_remRecordInfo()
		self.__class__.pagePfund.click_remSubmit()
		self.__class__.pagePfund.click_confirm2()

		time.sleep(1)
		if self.__class__.pagePfund.successFlag():
			addImage(self.driver.get_screenshot_as_base64(),f'{productCode} 赎回成功')
			self.__class__.pagePfund.click_confirm3()
		else:
			addImage(self.driver.get_screenshot_as_base64(),f'{productCode} 赎回失败')
			self.assertTrue(0)

		logging.info(f' ========== 测试结束 pFund-02 私募基金赎回 {productCode} ========== ')

	def tearDown(self):
		pass

	@classmethod
	def tearDownClass(cls):
		logging.info(' ########## 私募基金下单测试结束 ########## ')

if __name__=='__main__':
	unittest.main()