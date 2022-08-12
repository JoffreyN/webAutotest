import logging,time
from selenium.webdriver.common.by import By
from .base import PageBase
from selenium.webdriver.common.action_chains import ActionChains

class PageSelfselected(PageBase):
	def __init__(self,driver):
		# 自选相关
		super().__init__(driver)

		# 自选元素块
		self.staredName=(By.XPATH,'//*[@class="wrap"]//*[@name="flip-list"]//*[@class="name"]')
		self.staredCode=(By.XPATH,'//*[@class="wrap"]//*[@name="flip-list"]//*[@class="bottom"]/span[1]')
		self.staredDel=(By.XPATH,'//*[@class="model"]/div[text()="删除"]')#需要先鼠标右键点击

		# K线图元素块

		# F10元素块

		# 股票信息元素块
		self.codeName=(By.XPATH,'//*[@class="stock-quote"]/div[@class="name"]')
		self.star=(By.XPATH,'//*[@class="stock-quote"]/div[@class="tags"]/span[contains(@title,"自选")]')

		# 买卖5档元素块

		# 交易元素块

	def get_staredstock(self):
		logging.info(f'获取自选股列表')
		staredstock=[]
		return dict(zip([ele.text.strip() for ele in self.findElements(self.staredCode)],[ele.text.strip() for ele in self.findElements(self.staredName)]))

	def unStar(self,stockName):
		logging.info(f'点击 取消自选')
		xpath=(By.XPATH,f'//*[@class="wrap"]//*[@name="flip-list"]//*[@class="name" and text()="{stockName}"]')
		ele=self.findElement(xpath)
		ActionChains(self.driver).context_click(ele).perform()
		self.findElement(self.staredDel).click()

	def click_star(self):
		logging.info(f'点击 添加自选')
		self.findElement(self.star).click()
		time.sleep(5)
