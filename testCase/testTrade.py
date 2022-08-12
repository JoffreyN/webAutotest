import time,logging,traceback,unittest,threading
from HTMLReport import ddt,addImage,no_retry

from common.parameter import ParameTestCase
from common.system_boss import inmoney_CMS
from business.login_out import login

from page.login_all import PageLogin
from page.header_bar import PageHeaderBar
from page.alert import PageAlert
from page.trade import PageTrade

from testData.data import accountPool,accBinding,tradeData

# @unittest.skip('跳过')
@ddt.ddt
class TestTrade(ParameTestCase):
	@classmethod
	def setUpClass(cls):
		logging.info(' ########## 股票交易测试开始 ########## ')
		# cls.pageLogin=PageLogin(cls.driver)
		cls.pageHeaderBar=PageHeaderBar(cls.driver)
		cls.pageAlert=PageAlert(cls.driver)
		cls.pageTrade=PageTrade(cls.driver)
		threading.Thread(target=inmoney_CMS,args=(cls.args.account,'HKD','20000',cls.args.env,1,)).start()
		threading.Thread(target=inmoney_CMS,args=(cls.args.account,'CNY','20000',cls.args.env,1,)).start()
		threading.Thread(target=inmoney_CMS,args=(cls.args.account,'USD','20000',cls.args.env,1,)).start()


	def setUp(self):
		pwd=accountPool[self.args.account]
		login(self.driver,(self.args.account,pwd))
		if '/#/trade' not in self.driver.current_url:
			self.__class__.pageHeaderBar.clickTrade()

	# @unittest.skip('跳过')
	# @ddt.data(*['竞价盘'])
	# @no_retry
	@ddt.data(*['特殊限价盘','竞价限价盘','限价盘','竞价盘','增强限价盘'])
	def test_CMBI_01(self,panName):
		'''股票交易买入港股'''
		stockCode=tradeData[self.args.account]['b']['HK'][0]
		logging.info(f' ========== 测试开始 CMBI-01 {panName} 股票交易买入港股 {stockCode} ========== ')
		start=time.perf_counter()
		self.__class__.pageTrade.input_search(stockCode)
		self.__class__.pageTrade.click_result()
		# time.sleep(1)
		self.__class__.pageTrade.click_panSelect()
		self.__class__.pageTrade.click_panType(panName)
		# time.sleep(1)
		canBuy=self.__class__.pageTrade.get_canBuy()
		ability=self.__class__.pageTrade.get_ability()
		self.assertGreater(canBuy,0)
		self.assertGreater(ability,0)
		# self.__class__.pageBuy.clickBuyPriceOne()
		# self.__class__.pageBuy.inputNum(1000)
		self.__class__.pageTrade.click_plus(1)
		self.__class__.pageTrade.click_buy()
		time.sleep(1)
		addImage(self.driver.get_screenshot_as_base64(),'点击买入后截图')
		self.__class__.pageTrade.click_confirm('确认买入')
		antmsg=self.__class__.pageAlert.getAntMsg()
		logging.info(f'获取提示信息: {antmsg}')
		time.sleep(1)
		self.driver.refresh()
		orderOne_stock=self.__class__.pageTrade.get_orderOne(2)
		orderOne_panName=self.__class__.pageTrade.get_orderOne(11)
		self.assertIn(stockCode,orderOne_stock,f'测试不通过！输入的股票代码与委托结果不一致：{stockCode} {orderOne_stock}')
		self.assertIn(panName,orderOne_panName,f'测试不通过！选择的盘类型与委托结果不一致：{panName} {orderOne_panName}')
		
		logging.info(f'交易用例耗时：{round(time.perf_counter()-start,2)} 秒')
		logging.info(f' ========== 测试结束 CMBI-01 {panName} 股票交易买入港股 {stockCode} ========== ')


	def tearDown(self):
		pass

	@classmethod
	def tearDownClass(cls):
		logging.info(' ########## 股票交易测试结束 ########## ')

if __name__=='__main__':
	unittest.main()



