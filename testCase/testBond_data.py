import time,logging,traceback,unittest
from HTMLReport import ddt,addImage,no_retry
from common.parameter import ParameTestCase
from common.apiCenter import addHOld_ttl

from business.login_boss import login_boss
from page.appadmin.bond import PageBond

from testData.data import bondAcc,bond_data_uat
from config import bossAcc

# @unittest.skip('跳过')
@ddt.ddt
class TestBond_data(ParameTestCase):
	@classmethod
	def setUpClass(cls):
		logging.info(' ########## 债券申购测试开始 ########## ')
		cls.pageBond=PageBond(cls.driver)
		login_boss(cls.driver,bossAcc[cls.args.env],cls.args.env)
		cls.driver.get(f"http://{cls.args.env}-****.****.*****/corporate/onboard/list")
		cls.driver.set_window_size(1258,1329)
		
	def setUp(self):
		self.driver.get(f'http://{self.args.env}-****.****.*****/frame/body/load?link_id=522')
		time.sleep(3)
		self.driver.switch_to.frame("boss-frame")

	# @unittest.skip('跳过')
	@no_retry
	@ddt.data(*bond_data_uat)
	def test_Bond_01(self,item):
		'''债券申购金额数据测试'''
		productCode='Bbg2022040701USD'
		logging.info(f' ========== 测试开始 Bond-01 债券申购 数量:{item[0]} orderPrice:{item[1]} 实收佣金:{item[2]} ========== ')
		self.__class__.pageBond.click_add()
		time.sleep(3)
		self.__class__.pageBond.input_account(bondAcc[self.args.env])
		time.sleep(2)
		self.__class__.pageBond.click_confirm()
		time.sleep(2)
		self.__class__.pageBond.click_search()
		time.sleep(3)
		self.__class__.pageBond.input_productCode(productCode)
		self.__class__.pageBond.click_searchYes()
		time.sleep(3)
		self.__class__.pageBond.click_result()
		time.sleep(3)
		# minimum=self.__class__.pageBond.get_minimum()
		self.__class__.pageBond.input_buyAmount(amount=item[0],f=1)
		self.__class__.pageBond.input_price(price=item[1])
		self.__class__.pageBond.input_rate1(rate=item[2])
		self.__class__.pageBond.click_checkBox()
		self.__class__.pageBond.input_recordInfo()
		# self.__class__.pageBond.input_clarification()
		self.__class__.pageBond.input_vcWitness()
		self.__class__.pageBond.click_submit()
		self.__class__.pageBond.click_confirm2()
		time.sleep(1)
		if self.__class__.pageBond.successFlag():
			addImage(self.driver.get_screenshot_as_base64(),f'{productCode} 申购成功')
			self.__class__.pageBond.click_confirm3()
		else:
			addImage(self.driver.get_screenshot_as_base64(),f'{productCode} 申购失败')
			self.assertTrue(0)
		logging.info(f' ========== 测试结束 Bond-01 债券申购 数量:{item[0]} orderPrice:{item[1]} 实收佣金:{item[2]} ========== ')



	def tearDown(self):
		pass

	@classmethod
	def tearDownClass(cls):
		logging.info(' ########## 债券申购测试结束 ########## ')

if __name__=='__main__':
	unittest.main()