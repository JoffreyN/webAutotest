import time,logging,traceback,unittest,threading
from HTMLReport import ddt,addImage,no_retry

from common.parameter import ParameTestCase
from common.system_boss import inmoney_CMS
from business.login_out import login

from page.login_all import PageLogin
from page.header_bar import PageHeaderBar
from page.alert import PageAlert
from page.selfSelected import PageSelfselected

from testData.data import accountPool,accBinding

# @unittest.skip('跳过')
@ddt.ddt
class TestSelfselected(ParameTestCase):
	@classmethod
	def setUpClass(cls):
		logging.info(' ########## 自选测试开始 ########## ')
		# cls.pageLogin=PageLogin(cls.driver)
		cls.pageHeaderBar=PageHeaderBar(cls.driver)
		cls.pageAlert=PageAlert(cls.driver)
		cls.pageSelfselected=PageSelfselected(cls.driver)

	def setUp(self):
		pwd=accountPool[self.args.account]
		login(self.driver,(self.args.account,pwd))
		self.__class__.pageHeaderBar.clickStocks()

	def __star(self,stockCode):
		self.__class__.pageHeaderBar.input_keyword(stockCode)
		self.__class__.pageHeaderBar.click_resultOne()
		time.sleep(3)
		self.__class__.pageSelfselected.click_star()
		self.driver.refresh()
		stared=self.__class__.pageSelfselected.get_staredstock()
		self.assertIn(stockCode,stared.keys())
		return stared

	def __unStar(self,stockCode,stockName):
		self.__class__.pageSelfselected.unStar(stockName)
		self.driver.refresh()
		self.assertNotIn(stockCode,self.__class__.pageSelfselected.get_staredstock().keys())

	# @unittest.skip('跳过')
	# @no_retry
	@ddt.data(*['00700','BILI','600036','300750','01458'])
	def test_CMBI_01(self,stockCode):
		'''添加/删除自选'''
		logging.info(f' ========== 测试开始 CMBI-01 添加/删除自选 {stockCode} ========== ')
		stared=self.__class__.pageSelfselected.get_staredstock()
		if stockCode in stared.keys():
			self.__unStar(stockCode,stared[stockCode])
			self.__star(stockCode)
		else:
			stared=self.__star(stockCode)
			self.__unStar(stockCode,stared[stockCode])
		logging.info(f' ========== 测试结束 CMBI-01 添加/删除自选 {stockCode} ========== ')


	def tearDown(self):
		pass

	@classmethod
	def tearDownClass(cls):
		logging.info(' ########## 自选测试结束 ########## ')

if __name__=='__main__':
	unittest.main()



