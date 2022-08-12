import time,logging,traceback,unittest
from HTMLReport import ddt,addImage,no_retry
from common.parameter import ParameTestCase
from common.apiCenter import addHOld_ttl
from common.system_boss import addPfund,queryPfundCode,login_boss_api,getPower
from common.system_pmo import *
from common.tools import save_to_excel

from business.login_boss import login_boss
from page.appadmin.pFund import PagePfund

from testData.data import fundAcc
from config import bossAcc

# @unittest.skip('跳过')
@ddt.ddt
class TestPfund_uat(ParameTestCase):
	@classmethod
	def setUpClass(cls):
		logging.info(' ########## 私募基金下单测试开始 ########## ')
		cls.pagePfund=PagePfund(cls.driver)
		login_boss(cls.driver,bossAcc[cls.args.env],cls.args.env)
		cls.driver.set_window_size(1258,1329)
		login_boss_api(cls.args.env)

		cls.fundNameList=[]
		for curr in ['HKD','USD','CNY']:
			# for i in range(3):
			cls.fundNameList.append(addPfund(curr,cls.args.env))
			time.sleep(1)
		time.sleep(60)
		cls.pfundURL=f'http://{cls.args.env}-****.****.*****/frame/body/load?link_id=516'
		
	def setUp(self):
		pass

	# @unittest.skip('跳过')
	@no_retry
	def test_pFund_01(self):
		'''私募基金下单'''
		fail=0
		for pfundName in self.__class__.fundNameList:
			try:
				self.driver.get(self.__class__.pfundURL)
				time.sleep(3)
				self.driver.switch_to.frame('boss-frame')
				productCode=queryPfundCode(pfundName,self.args.env)
				logging.info(f' ========== 测试开始 pFund-01 私募基金申购 {productCode} ========== ')
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
				minimum=self.__class__.pagePfund.get_minimum()
				power=getPower(fundAcc[self.args.env],productCode,types='pFundOrder',env=self.args.env)
				logging.info(f'申购前购买力: {power}')

				amount=self.__class__.pagePfund.input_buyAmount(minimum)
				self.__class__.pagePfund.losefocus()
				time.sleep(3)
				self.__class__.pagePfund.input_rate1()
				self.__class__.pagePfund.input_rate2()
				self.__class__.pagePfund.click_checkBox()
				self.__class__.pagePfund.select_custRatioRisk()
				self.__class__.pagePfund.input_middleSuggest()
				self.__class__.pagePfund.input_productMayRisk()
				self.__class__.pagePfund.myInput('录音编号 ',self.__class__.pagePfund.recordInfo,'recordInfo from AutoTest')
				self.__class__.pagePfund.myInput('见证职员名称 ',self.__class__.pagePfund.staffName,'AutoTest')


				self.__class__.pagePfund.click_submit()
				self.__class__.pagePfund.click_confirm2()
				# time.sleep(3)
				# self.__class__.pagePfund.click_confirm()
				time.sleep(1)
				if self.__class__.pagePfund.successFlag():
					logging.info('申购成功')
					addImage(self.driver.get_screenshot_as_base64(),f'{productCode} 申购成功')
					self.__class__.pagePfund.click_confirm3()
					time.sleep(3)
					power2=getPower(fundAcc[self.args.env],productCode,types='pFundOrder',env=self.args.env)
					logging.info(f'申购后购买力: {power2}')
					self.assertNotEqual(power,power2)

					mergerOrder(queryOrders(productCode))
					groupId=get_groupId(productCode,self.args.env)
					complete(groupId,self.args.env)
					status='Fail' if 'CNY' in productCode else 'Success'
					save_to_excel(groupId,productCode,pfundName,amount,side='BUY',status=status)
					pFund_upload()
					time.sleep(2)
					complete_confirm(groupId,self.args.env)

				else:
					fail=+1
					logging.info('申购失败')
					addImage(self.driver.get_screenshot_as_base64(),f'{productCode} 申购失败')
				logging.info(f' ========== 测试结束 pFund-01 私募基金申购 {productCode} ========== ')
			except:
				fail=+1
				logging.error(traceback.format_exc())
		self.assertFalse(fail)

	# @unittest.skip('跳过')
	@no_retry
	def test_pFund_02(self):
		'''私募基金赎回'''
		fail=0
		for pfundName in self.__class__.fundNameList:
			try:
				self.driver.get(self.__class__.pfundURL)
				# http://test-boss.cmbi.online/frame/body/load?link_id=534
				time.sleep(3)
				self.driver.switch_to.frame('boss-frame')
				productCode=queryPfundCode(pfundName,self.args.env)
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
				amount=self.__class__.pagePfund.input_units()
				self.__class__.pagePfund.input_redemptionFeeRate()
				# self.__class__.pagePfund.input_remRecordInfo()
				self.__class__.pagePfund.click_checkBox()
				self.__class__.pagePfund.click_remSubmit()
				self.__class__.pagePfund.click_confirm2()

				time.sleep(1)
				if self.__class__.pagePfund.successFlag():
					addImage(self.driver.get_screenshot_as_base64(),f'{productCode} 赎回成功')
					self.__class__.pagePfund.click_confirm3()
					time.sleep(3)

					mergerOrder(queryOrders(productCode,'SELL'))
					groupId=get_groupId(productCode,self.args.env)
					complete(groupId,self.args.env)
					status='Fail' if 'CNY' in productCode else 'Success'
					save_to_excel(groupId,productCode,pfundName,amount,side='SELL',status=status)
					pFund_upload()
					time.sleep(2)
					complete_confirm(groupId,self.args.env)

				else:
					fail+=1
					addImage(self.driver.get_screenshot_as_base64(),f'{productCode} 赎回失败')
				logging.info(f' ========== 测试结束 pFund-02 私募基金赎回 {productCode} ========== ')
			except:
				fail+=1
				logging.error(traceback.format_exc())
		self.assertFalse(fail)

	def tearDown(self):
		pass

	@classmethod
	def tearDownClass(cls):
		logging.info(' ########## 私募基金下单测试结束 ########## ')

if __name__=='__main__':
	unittest.main()