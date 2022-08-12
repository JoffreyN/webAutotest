from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.touch_actions import TouchActions
from selenium.webdriver.common.by import By
from HTMLReport import addImage
import traceback,time,logging
import socket,urllib3
from common.seleniumError import *


class PageBase(object):
	def __init__(self,driver):
		self.driver=driver

	def findElement(self,loc,screen=True,timeout=15,until='click'):
		try:
			if until=='click':
				WebDriverWait(self.driver,timeout,0.5).until(EC.element_to_be_clickable(loc))
			elif until=='located':
				WebDriverWait(self.driver,timeout,0.5).until(EC.presence_of_element_located(loc))
			return self.driver.find_element(*loc)
		except (SCETE,SCENSEE):
			msg=f'{self} 页面未找到 {loc} 元素'
			logging.error(msg)
			if screen:addImage(self.driver.get_screenshot_as_base64(),msg,traceback.format_exc())
			return
		except (socket.timeout,urllib3.exceptions.ReadTimeoutError):			
			raise Exception(f'{self} 页面发生timeout异常 元素 {loc} \n{traceback.format_exc()}')
		except:
			msg=f'{self} 页面发生其它异常 元素 {loc} \n{traceback.format_exc()}'
			logging.error(msg)
			if screen:addImage(self.driver.get_screenshot_as_base64(),*msg.split('\n',1))
			return
 
	def findElements(self,loc,screen=True,timeout=15,until='click'):
		try:
			if until=='click':
				WebDriverWait(self.driver,timeout,0.5).until(EC.element_to_be_clickable(loc))
			elif until=='located':
				WebDriverWait(self.driver,timeout,0.5).until(EC.presence_of_element_located(loc))
			return self.driver.find_elements(*loc)
		except (SCETE,SCENSEE):
			msg=f'{self} 页面未找到 {loc} 元素'
			logging.error(msg)
			if screen:addImage(self.driver.get_screenshot_as_base64(),msg,traceback.format_exc())
			return
		except (socket.timeout,urllib3.exceptions.ReadTimeoutError):
			
			raise Exception(f'{self} 页面发生timeout异常 元素 {loc} \n{traceback.format_exc()}')
		except:
			msg=f'{self} 页面发生其它异常 元素 {loc} \n{traceback.format_exc()}'
			logging.error(msg)
			if screen:addImage(self.driver.get_screenshot_as_base64(),*msg.split('\n',1))
			return

	# def myTap(self,ele):
	# 	TouchActions(self.driver).tap(ele).perform()
	
	def myClick(self,msg,loc,until='click',scroll=0):
		logging.info(f'点击 {msg}')
		ele=self.findElement(loc,until=until)
		if scroll:
			self.driver.execute_script("arguments[0].scrollIntoView();",ele)
		ele.click()

	def myInput(self,msg,loc,value):
		logging.info(f'{msg}输入 {value}')
		self.findElement(loc).send_keys(value)

	def clickByScript(self,ele):
		self.driver.execute_script("arguments[0].click();",ele)

	def clickByEleXY(self,ele):
		x,y=ele.location.values()
		h,w=ele.size.values()
		# logging.info( x,y,h,w)
		self.driver.tap([(int(x+w/2),int(y+h/2))])

	def isEleExists(self,loc,timeout=10,screen=0):
		try:
			WebDriverWait(self.driver,timeout,0.5).until(EC.presence_of_element_located(loc))
			if self.driver.find_element(*loc):return 1
			else:return 0
		except (SCETE,SCENSEE):
			msg=f'{self} 找不到元素 {loc}'
			logging.error(msg)
			if screen:addImage(self.driver.get_screenshot_as_base64(),msg,traceback.format_exc())
			return 0
		except (socket.timeout,urllib3.exceptions.ReadTimeoutError):
			
			raise Exception(f'{self} 页面发生timeout异常 元素 {loc} \n{traceback.format_exc()}')
		except:
			logging.error(f'{self} 页面发生其它异常 元素 {loc} \n{traceback.format_exc()}')
			return 0


