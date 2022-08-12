import logging,time
from selenium.webdriver.common.by import By
from .base import PageBase

class PageTrade(PageBase):
	def __init__(self,driver):
		# 交易相关
		super().__init__(driver)

		self.search=(By.XPATH,'//*[@class="stock-search"]/input')
		self.clear=(By.CSS_SELECTOR,'.clear')
		self.confirm=(By.XPATH,'//span[contains(text(),"确认")]/..')

		#买卖元素块
		self.result=(By.CLASS_NAME,'result-item')#第0个
		self.panSelect=(By.CLASS_NAME,'ant-select-selection-item')
		self.panType=(By.XPATH,'//*[@class="rc-virtual-list-holder-inner"]/div')

		self.minus=(By.XPATH,'//*[@class="icon minus"]')# 价格减或数量减
		self.plus=(By.XPATH,'//*[@class="icon plus"]')# 价格加或数量加
		self.canBuy=(By.XPATH,'//*[@class="can-buy"]/span')
		self.ability=(By.XPATH,'//*[@class="ability"]/span')
		self.btn_buy=(By.XPATH,'//button[contains(@class," buy")]')
		self.btn_sub=(By.XPATH,'//button[contains(@class,"btn-sub")]')#切换买入/卖出

		#盘口元素块
		self.bs_b=(By.XPATH,'//div[contains(@class,"buy bs-container")]//span')#第0个表示买1
		self.bs_s=(By.XPATH,'//div[contains(@class,"sell bs-container")]//span')#第0个表示卖1
		
		#K线图元素块
		
		#K持仓元素块
		
		#订单元素块


	def click_clear(self,n=0):
		logging.info(f'点击 清除')
		self.findElements(self.clear)[n].click()

	def input_search(self,keyword,n=0):
		logging.info(f'输入关键词 {keyword}')
		ele=self.findElements(self.search)[n]
		ele.clear()
		ele.send_keys(keyword)

	def click_confirm(self,msg='确认'):
		logging.info(f'点击 {msg}')
		self.findElement(self.confirm).click()

	def click_result(self):
		logging.info(f'点击 第一条搜索结果')
		self.findElements(self.result)[0].click()

	def click_panSelect(self):
		logging.info(f'点击选择盘类型')
		self.myTap(self.findElement(self.panSelect))

	def click_panType(self,panName):
		panName_dict={'增强限价盘':0,'特殊限价盘':1,'竞价限价盘':2,'限价盘':3,'竞价盘':4}
		logging.info(f'点击 {panName}')
		self.findElements(self.panType)[panName_dict[panName]].click()

	def click_minus(self,n=0):
		msg_dit={0:'价格',1:'数量'}
		logging.info(f'点击 {msg_dit[n]} 减')
		self.findElements(self.minus,until='located')[n].click()

	def click_plus(self,n=0):
		msg_dit={0:'价格',1:'数量'}
		logging.info(f'点击 {msg_dit[n]} 加')
		self.findElements(self.plus,until='located')[n].click()

	def get_canBuy(self):
		logging.info(f'获取可买')
		canBuy=self.findElement(self.canBuy).text.strip()
		logging.info(f'可买 {canBuy}')
		return float(canBuy.replace(',',''))

	def get_ability(self):
		logging.info(f'获取购买力')
		ability=self.findElement(self.ability).text.strip()
		logging.info(f'购买力 {ability}')
		return float(ability.replace(',',''))
	
	def click_buy(self):
		logging.info(f'点击 买入')
		self.findElement(self.btn_buy).click()

	def click_sub(self):
		logging.info(f'点击 切换买入/卖出')
		self.findElement(self.btn_sub).click()

	def get_bs_b(self,n=0):
		logging.info(f'获取 买 {n+1} 价')
		return self.findElements(self.bs_b)[n].text.strip()

	def get_bs_s(self,n=0):
		logging.info(f'获取 卖 {n+1} 价')
		return self.findElements(self.bs_s)[n].text.strip()

	def get_orderOne(self,m=2,n=0):
		# n=0 表示第一条订单记录
		m_dict={2:'股票代码',11:'盘类型'}
		logging.info(f'获取第 {n+1} 条订单记录的 {m_dict[m]}')
		xpath=f'//tr[contains(@class,"ant-table-row")]/td[{m}]'
		return self.findElements((By.XPATH,xpath))[n].text.strip()

	# def smsFlag(self):
	# 	return self.isEleExists(self.btn_SMS,timeout=3)




















