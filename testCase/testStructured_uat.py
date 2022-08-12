import time,logging,traceback,unittest
from HTMLReport import ddt,addImage,no_retry
from common.parameter import ParameTestCase
from common.apiCenter import addHOld_ttl
from common.system_boss import add_structure,login_boss_api,getPower
from common.system_pmo import *

from business.login_boss import login_boss
from page.appadmin.structured import PageStructured

from testData.data import structuredPool_test,structuredPool_uat,structuredAcc
from config import bossAcc

# @unittest.skip('跳过')
@ddt.ddt
class TestStructured_uat(ParameTestCase):
	@classmethod
	def setUpClass(cls):
		logging.info(' ########## 结构化交易下单测试开始 ########## ')
		cls.pageStructured=PageStructured(cls.driver)
		login_boss(cls.driver,bossAcc[cls.args.env],cls.args.env)
		cls.driver.set_window_size(1258,1329)
		login_boss_api(cls.args.env)
		
		# cls.structPRD=['S20220729S108USD']
		cls.structPRD=[]
		for curr in ['HKD','USD','CNY']:
			# for i in range(3):
			cls.structPRD.append(add_structure(curr,cls.args.env))
			time.sleep(1)
		time.sleep(60)
		cls.structURL=f'http://{cls.args.env}-****.****.*****/frame/body/load?link_id=524'

	def setUp(self):
		pass

	# @unittest.skip('跳过')
	@no_retry
	def test_Structured_01(self):
		'''结构化交易下单'''
		fail=0
		for struct in self.__class__.structPRD:
			try:
				self.driver.get(self.__class__.structURL)
				time.sleep(3)
				self.driver.switch_to.frame('boss-frame')
				logging.info(f' ========== 测试开始 Structured-01 结构化交易申购 {struct} ========== ')
				self.__class__.pageStructured.click_add()
				time.sleep(3)
				self.__class__.pageStructured.input_account(structuredAcc[self.args.env])
				time.sleep(2)
				self.__class__.pageStructured.click_confirm()
				time.sleep(2)
				self.__class__.pageStructured.click_search()
				time.sleep(3)
				self.__class__.pageStructured.input_productCode(struct)
				self.__class__.pageStructured.click_searchYes()
				time.sleep(3)
				self.__class__.pageStructured.click_result()
				time.sleep(3)
				minimum=self.__class__.pageStructured.get_minimum()
				power=getPower(structuredAcc[self.args.env],struct,types='spOrder',env=self.args.env)
				logging.info(f'申购前购买力: {power}')

				self.__class__.pageStructured.input_buyAmount(minimum)
				# self.__class__.pageStructured.input_price()
				self.__class__.pageStructured.input_rate1()
				self.__class__.pageStructured.click_checkBox()

				self.__class__.pageStructured.select_custRatioRisk()
				self.__class__.pageStructured.input_middleSuggest()
				self.__class__.pageStructured.input_productMayRisk()
				self.__class__.pageStructured.myInput('见证职员 ',self.__class__.pageStructured.staffName,'Autotest')
				self.__class__.pageStructured.myInput('录音编号 ',self.__class__.pageStructured.recordInfo,'recordInfo from AutoTest')

				self.__class__.pageStructured.click_submit()
				# self.__class__.pageStructured.click_confirm2()
				time.sleep(1)
				if self.__class__.pageStructured.successFlag():
					addImage(self.driver.get_screenshot_as_base64(),f'{struct} 申购成功')
					self.__class__.pageStructured.click_confirm3()
					time.sleep(3)
					power2=getPower(structuredAcc[self.args.env],struct,types='spOrder',env=self.args.env)
					logging.info(f'申购后购买力: {power2}')
					self.assertNotEqual(power,power2)


					mergerOrder_struct(queryOrders_struct(struct))
					groupId=get_groupId_struct(struct,self.args.env)
					edit_struct(groupId,self.args.env)
					complete_struct(groupId,self.args.env)

				else:
					fail+=1
					addImage(self.driver.get_screenshot_as_base64(),f'{struct} 申购失败')
				logging.info(f' ========== 测试结束 Structured-01 结构化交易申购 {struct} ========== ')
			except:
				fail+=1
				logging.error(traceback.format_exc())
		self.assertFalse(fail)

	# @unittest.skip('跳过')
	@no_retry
	def test_Structured_02(self):
		'''结构化交易赎回'''
		fail=0
		for struct in self.__class__.structPRD:
			try:
				self.driver.get(self.__class__.structURL)
				time.sleep(3)
				self.driver.switch_to.frame('boss-frame')
				logging.info(f' ========== 测试开始 pFund-02 结构化交易赎回 {struct} ========== ')
				addHOld_ttl(structuredAcc[self.args.env],struct,'5000','SPMK','D',self.args.env)

				self.__class__.pageStructured.click_add()
				time.sleep(3)
				self.__class__.pageStructured.input_account(structuredAcc[self.args.env])
				time.sleep(2)
				self.__class__.pageStructured.click_confirm()
				time.sleep(2)

				self.__class__.pageStructured.click_redemption()
				self.__class__.pageStructured.click_search(1)
				time.sleep(3)
				self.__class__.pageStructured.input_productCode(struct)
				self.__class__.pageStructured.click_searchYes()
				time.sleep(3)
				self.__class__.pageStructured.click_result()
				time.sleep(3)
				self.__class__.pageStructured.input_units()
				self.__class__.pageStructured.input_price(n=1)
				# self.__class__.pageStructured.input_rate1(1)
				self.__class__.pageStructured.click_remCheckBox()

				# self.__class__.pageStructured.input_remRecordInfo()
				self.__class__.pageStructured.click_remSubmit()
				# self.__class__.pageStructured.click_confirm2()

				time.sleep(1)
				if self.__class__.pageStructured.successFlag():
					addImage(self.driver.get_screenshot_as_base64(),f'{struct} 赎回成功')
					self.__class__.pageStructured.click_confirm3()
					time.sleep(3)

					mergerOrder_struct(queryOrders_struct(struct,'SELL'))
					groupId=get_groupId_struct(struct,self.args.env)
					edit_struct(groupId,self.args.env,'SELL')
					complete_struct(groupId,self.args.env)

				else:
					fail+=1
					addImage(self.driver.get_screenshot_as_base64(),f'{struct} 赎回失败')
				logging.info(f' ========== 测试结束 pFund-02 结构化交易赎回 {struct} ========== ')
			except:
				fail+=1
				logging.error(traceback.format_exc())
		self.assertFalse(fail)

	def tearDown(self):
		pass

	@classmethod
	def tearDownClass(cls):
		logging.info(' ########## 结构化交易下单测试结束 ########## ')

if __name__=='__main__':
	unittest.main()