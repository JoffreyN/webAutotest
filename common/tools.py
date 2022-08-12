import time,datetime,logging,os,sys

def save_to_excel(groupId,prdCode,prdName,amount,side='BUY',status='Success'):
	from openpyxl import load_workbook
	excel=load_workbook('testData/pfund_data.xlsx')
	sheet=excel.active
	sheet['A2']=groupId
	sheet['B2']=prdCode
	sheet['C2']=prdName
	sheet['D2']=side
	sheet['E2']=amount
	sheet['F2']=amount
	# sheet['G2']=
	sheet['H2']=time.strftime("%Y-%m-%d")
	sheet['I2']=status
	excel.save('testData/tmp.xlsx')

def encryption(jsonData,keyType='APP'):
	keyDict={'APP':'*********','H5':'********'}
	timestamp=str(int(1000*time.time()))
	jsonData=dict(sorted(jsonData.items(),key=operator.itemgetter(0),reverse=False))# 排序
	msg=json.dumps(jsonData).replace(" ","")+timestamp
	signature=hmac.new(keyDict[keyType].encode('utf-8'),msg.encode('utf-8'),hashlib.md5).hexdigest()
	return timestamp,signature

def getSoup(driver):
	from bs4 import BeautifulSoup
	html=driver.page_source
	soup=BeautifulSoup(html,'lxml')
	return soup

def encode_md5(string):
	# for TTL resetpwd
	import hashlib
	md5=hashlib.md5()
	md5.update(string.encode(encoding='utf-8'))
	return md5.hexdigest()

def scrollByXpath(driver,xpath):
	xpath=xpath.replace("'",'"')
	js1="function getElementByXpath(path) {return document.evaluate(path,document,null,XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;};"
	js2=f"getElementByXpath('{xpath}').scrollIntoView();"
	driver.execute_script(js1+js2)


def coordinate(xy0,size1,size0=(1440,2960)):
	x1=int(xy0[0]/size0[0]*size1[0])
	y1=int(xy0[1]/size0[1]*size1[1])
	return x1,y1

def maxVersion(v1,v2):
	v1List=v1.split('.')
	v2List=v2.split('.')
	maxLen=max(len(v1List),len(v2List))
	for i in range(maxLen):
		str1=v1List[i];str2=v2List[i]
		if i==maxLen-1:
			while 1:
				if len(str1)<len(str2):str1=f'{str1}0'
				elif len(str1)>len(str2):str2=f'{str2}0'
				elif len(str1)==len(str2):break
		int1=int(str1);int2=int(str2)
		if int1>int2:return v1
		elif int1<int2:return v2
		else:
			if i==maxLen-1:return v1

def isTradeTime(timeNow=None,market='HK'):
	#传入时间戳
	from chinese_calendar import is_workday
	if not timeNow:timeNow=time.time()
	date,weekDay=time.strftime('%Y%m%d %w').split()
	yestodate_date=datetime.datetime.now()+datetime.timedelta(days = -1)
	yestodate=f'{yestodate_date.year}{yestodate_date.month}{yestodate_date.day}'
	resp=is_workday(datetime.date(int(date[:4]),int(date[4:6]),int(date[6:])))# 节假日返回 False
	if (not resp) or (weekDay in ['0','6']):#周六日休市
		return 0
	else:
		if market=='HK':
			start1=time.mktime(time.strptime(f'{date} 09:30:00','%Y%m%d %X'))
			stop1=time.mktime(time.strptime(f'{date} 12:00:00','%Y%m%d %X'))
			start2=time.mktime(time.strptime(f'{date} 13:00:00','%Y%m%d %X'))
			stop2=time.mktime(time.strptime(f'{date} 16:00:00','%Y%m%d %X'))
		elif market=='A':
			start1=time.mktime(time.strptime(f'{date} 09:30:00','%Y%m%d %X'))
			stop1=time.mktime(time.strptime(f'{date} 11:30:00','%Y%m%d %X'))
			start2=time.mktime(time.strptime(f'{date} 13:00:00','%Y%m%d %X'))
			stop2=time.mktime(time.strptime(f'{date} 15:00:00','%Y%m%d %X'))
		elif market=='US':
			start1=time.mktime(time.strptime(f'{date} 21:30:00','%Y%m%d %X'))
			stop1=start1+6.5*60*60
			start2=time.mktime(time.strptime(f'{yestodate} 21:30:00','%Y%m%d %X'))
			stop2=start2+6.5*60*60
		timeNow_strf=time.strftime('%Y-%m-%d %X',time.localtime(timeNow))
		print(start1,stop1)
		if start1<timeNow<stop1 or start2<timeNow<stop2:
			print(f'当前时间 {timeNow_strf} 为 {market} 交易时间')
			return 1
		else:
			print(f'当前时间 {timeNow_strf} 为 {market} 菲交易时间')
			return 0

def moveFiles(reportName,ops='move'):
	from config import platform,genPath,webPath
	if platform=='darwin':
		cmd=f'mv {os.path.join(genPath,reportName)} {webPath}'
	elif platform=='win32':
		cmd=f'echo d | xcopy /r /y /e "{os.path.join(genPath,reportName)}" "{os.path.join(webPath,reportName)}"'
	os.system(cmd)

def saveFile(strs,out=1):
	from config import regFilePath
	if out:print(strs)
	try:
		with open(regFilePath,'a',encoding='utf-8') as f:
			f.write(f'{strs}\n')
	except FileNotFoundError:
		pass

def getWebDriver(setwindow=1,headless=0,browserType='chrome',wire=0):
	if wire:
		from seleniumwire import webdriver
	else:
		from selenium import webdriver

	chrome_option=webdriver.ChromeOptions()
	chrome_option.add_experimental_option('useAutomationExtension',False)#禁止显示“请停用以开发者……”
	# chrome_option.add_experimental_option('credentials_enable_service',False)#禁止显示“请停用以开发者……”
	chrome_option.add_experimental_option("prefs",{"credentials_enable_service":False,"profile.password_manager_enabled":False})#禁用“保存密码”弹出窗口
	chrome_option.add_experimental_option("excludeSwitches",['enable-automation'])#禁止显示“Chrome正受到自动化软件的控制”
	chrome_option.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) # 禁止加载图片
	chrome_option.add_experimental_option('useAutomationExtension', False) # 禁用扩展插件
	# options.add_argument("--disable-gpu") # 禁用gpu
	# chrome_option.add_experimental_option('w3c',False)
	if headless:chrome_option.add_argument('--headless')

	driver=webdriver.Chrome(options=chrome_option)
	# if setwindow:driver.set_window_size(1750,1300)
	driver.maximize_window()
	return driver

def sendMail(text,platformName,fromInfo=None,cusReceiver=None):
	import smtplib
	from email.header import Header
	from email.mime.text import MIMEText
	from email.utils import formataddr
	if cusReceiver:
		receiver,mailToCc=cusReceiver.split(),[]
	else:
		receiver=['CMBI-FINTECH@****.***.**']
		mailToCc=[]
	sender='CMBI-TEST@****.***.**'
	# username='CMBI-TEST@****.***.**'
	# password='****'
	subject=f'【{platformName}】PC端壹隆环球自动化测试报告'

	msg=MIMEText(text,'html','utf-8')
	msg['Subject']=Header(subject,'utf-8') #设置主题和格式
	if not fromInfo:fromInfo="webAutotest UI自动化测试"
	msg['From']=formataddr([fromInfo,sender])
	msg['To']=';'.join(receiver)
	msg['Cc']=';'.join(mailToCc)
	
	smtp=smtplib.SMTP('mail.****.***.**',25)
	# smtp=smtplib.SMTP_SSL('smtp.qq.com',465)
	# smtp.ehlo()
	# smtp.starttls()
	# smtp.login(username, password)
	smtp.sendmail(sender, receiver+mailToCc, msg.as_string())
	smtp.quit()
	logging.info(f'邮件发送成功')

def removeFile(filePath):
	try:
		os.remove(filePath)
	except FileNotFoundError:
		pass

def out(strings):
	sys.stdout.write(f'{strings}\r')
	sys.stdout.flush()

def saveCookie(cookie,file):
	sys.path.append('..')
	fpath='testData/cookie'
	if not os.path.exists(fpath):os.mkdir(fpath)
	with open(f'{fpath}/{file}','w',encoding='utf-8') as f:
		f.write(cookie)

def readCookie(file):
	sys.path.append('..')
	try:
		return open(f'testData/cookie/{file}').read().strip()
	except:
		logging.info(f'读取cookie文件失败: {file}')
		return '0'

