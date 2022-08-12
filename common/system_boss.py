import requests,logging,time,re,base64,simplejson
from random import randint
from bs4 import BeautifulSoup
from .tools import saveCookie,readCookie

def getConfig_boss(env):
	global host,head,uname,pwd
	host=f'http://{env}-boss.****.*****'
	uname='uatAdmin'
	pwd='Cmbi6688'
	head={
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
		'Cookie':'',
		'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
		'Connection':'close',
		'X-Requested-With':'XMLHttpRequest',
	}

def login_boss_api(env):
	global host,head,uname,pwd
	getConfig_boss(env)
	url=f'{host}/admin/adminUser/login'
	keys={"account":uname,"password":pwd,"vcode":""}
	for i in range(3):
		resp=requests.post(url,headers=head,data=keys)
		try:
			respJson=resp.json()
		except json.decoder.JSONDecodeError:
			logging.error(f'自动登录BOSS系统失败，登录接口返回异常: {resp.text}')
			continue
		if respJson['result']=='1':
			try:
				respCookie=resp.headers['set-cookie']
				head['Cookie']=''.join(re.findall(r'PHPSESSID=.+?;',respCookie)+re.findall(r'BOSS-SIGN=.+?;',respCookie))
			except KeyError:
				head['Cookie']='0'
			saveCookie(head['Cookie'],f'boss_{env}')
			return head['Cookie']
		else:
			logging.error(f'自动登录BOSS系统失败: {respJson}')
			logging.info(f'2秒后开始第 {i+1} 次重试...')
			time.sleep(2);head['Cookie']=''
	raise

def requests_boss(methmod,path,url=None,header=None,backType='json',env='uat',**kwargs):
	global host,head,uname,pwd
	getConfig_boss(env.lower())
	headers=header if header else head
	cookieLogined=readCookie(f'boss_{env}')
	if not url:url=f'{host}{path}'
	for i in range(5):
		headers['Cookie']=cookieLogined
		resp=requests.request(methmod,url,headers=headers,allow_redirects=True,**kwargs)
		print(f"debug: {resp.headers}")
		if 'admin/AdminUser' in resp.text or '/admin/login' in resp.text:
			logging.info(f'BOSS后台cookie失效，重新登录…')
			cookieLogined=login_boss_api(env)
			continue
		else:
			if backType=='json':
				try:
					result=resp.json()
				except:
					logging.error(f'{path}返回数据不是json {resp.text}')
					result=resp.text
					continue
			elif backType=='text':
				result=resp.text
			elif backType=='soup':
				# print(f'debug: {resp.text}')
				with open('temp.html','w',encoding='utf-8') as f:f.write(resp.text)
				result=BeautifulSoup(resp.text,'lxml')
			return result

########################################################################################################################################
def getCasherDeposite(account,env='test'):
	# 根基账户号查询资金存入申请列表
	path='/casher/deposite/list'
	key={'step_id':'1987040','aecode':'','accountid':account}
	soup=requests_boss('GET',path,backType='soup',env=env,params=key)
	approveIdList=[]
	for tr in soup.select('tr'):
		try:
			approveIdList.append(tr.select('td')[-1].select_one('a')['href'])
		except IndexError:
			pass
	return approveIdList

def approve_submit(approveIdList,env='test'):
	# 提交资金审核通过
	if isinstance(approveIdList,str):approveIdList=[approveIdList]
	key={'current_step_id':'1987040','to_step_id':'pass','approve_note':''}
	for approveId in approveIdList:
		respJson=requests_boss('POST',path,backType='json',env=env,data=key)
		logging.info(f'{approveId}审核结果:{respJson}')


########################################################################################################################################
def getSMScode(phone,env='uat',n=0):
	if n:return '8'*n
	global host,head,uname,pwd
	getConfig_boss(env.lower())
	param={
		'key':'mobile',
		'search':phone,
		'begin_date':'',
		'end_date':'',
	}
	url=f'{host}/admin/appSendRecord/list'
	cookieLogined=readCookie(f'boss_{env}')
	for i in range(5):
		head['Cookie']=cookieLogined;resultList=[]
		head['X-Requested-With']='XMLHttpRequest'
		resp=requests.get(url,params=param,headers=head)
		try:
			respJson=resp.json()
		except:
			print(resp.content)
			raise Exception(f'获取验证码失败')
		if respJson['result']=='302':
			logging.info('boss后台cookie失效，重新登录…')
			cookieLogined=login_boss_api(env)
			continue
		elif respJson['result']=='1':
			resultList=respJson['data']['dataList']['list']
			if resultList:
				smsCode=filterSMScode(resultList)
				if smsCode:
					return smsCode
				else:
					logging.info(f'boss后台未查询到 {phone} 5分钟内的验证码，2秒后重试…')
					time.sleep(2)
	raise

def filterSMScode(resultList):
	for result in resultList:
		if int(time.time())-time.mktime(time.strptime(result['createdAt'],'%Y-%m-%d %X'))<300:#5分钟内的
			try:
				return re.findall(r'\d{4,6}',result['content'])[0]
			except IndexError:
				continue
	return 0

########################################################################################################################################
def getMailRecord(account,env='uat',start_date=None,end_date=None,keyword='登录通知',timeLimit=180):
	date=time.strftime("%Y-%m-%d")
	if not start_date:start_date=date
	if not end_date:end_date=date
	param={
		'key':'accountid',
		'search':account,
		'start_date':start_date,
		'end_date':end_date,
	}
	path='/panel/mailRecord/list'
	soup=requests_boss('GET',path,backType='soup',env=env,params=param)
	mailRecord=[]
	for tr in soup.select_one('table').select_one('tbody').select('tr'):
		acc=tr.select('td')[1].text.strip()
		mailTxt=tr.select('td')[3].text.strip()
		sendTime=tr.select('td')[4].text.strip()
		mailid=tr.select('td')[-1].select_one('a')['href'].split('=')[-1]
		if (keyword in mailTxt) and (acc==account) and (int(time.time())-time.mktime(time.strptime(sendTime,'%Y-%m-%d %X'))<timeLimit):#3分钟内的:
			mailRecord.append((acc,mailTxt,sendTime,mailid))
	return mailRecord
		
########################################################################################################################################
# 修改账户手机号
def cmsClientPhone(account,env='uat'):
	# 查询客户信息手机信息 返回 edit_id
	path=f'/cms/cmsClientPhone/refreshAccount?accountid={account}'
	soup=requests_boss('GET',path,backType='soup',env=env)
	result=soup.select('td')[3].select_one('a')['href'].split('=')[-1]
	return result

def editPhone(account,newPhone,env='uat'):
	# 修改客户手机号
	edit_id=cmsClientPhone(account,env)
	path=f'/cms/cmsClientPhone/edit?id={edit_id}'
	key={
		'id':edit_id,
		'phone_type':'Mobile',
		'contact_type_phone':'2FA',
		'phone_number_countrycode':'86',
		'phone_number_phonenumber':newPhone,
	}
	respJson=requests_boss('POST',path,backType='json',env=env,data=key)
	logging.info(f'修改手机号 结果: {respJson}')

########################################################################################################################################
# cms重置密码
def cms_resetpwd(account,env='uat'):
	path='/panel/selfReset/save'
	key={
		'accountid':account,
		'verifyway':'客户邮件',
		'is_notify':'1',
	}
	respJson=requests_boss('POST',path,backType='json',env=env,data=key)
	logging.info(f'cms重置密码 结果: {respJson}')
	# {'result': '1', 'message': 'success', 'data': {'business_id': '77414'}, 'now': '2021-08-16 16:25:28'}
	return respJson

def getPwd_from_mail(mailid,env='uat',mod='reset'):
	path=f'/panel/mailRecord/view?id={mailid}'
	soup=requests_boss('GET',path,backType='soup',env=env)
	if mod=='reset':# 获取重置的密码
		pwd=soup.select('strong')[1].text
	elif mod=='first':# 获取初始密码
		pwd=soup.select('td')[1].text
	return pwd

########################################################################################################################################
# 开户时证件ocr开关
def switch_ocr(value,env='uat'):
	path='/master/masterSetting/edit'
	key={
		'id':'70',
		'key_code':'OCR_SWITCH',
		'key_value':value,
		'remark':'OCR是否开启开关(针对香港身份证/香港永久身份证/护照/港澳通行证) off-关闭，on-开启',
	}
	respJson=requests_boss('POST',path,backType='json',env=env,data=key)
	logging.info(f'ocr开关修改 结果: {respJson}')
	return respJson

########################################################################################################################################
def cmsSearch_quick(account,env='uat'):
	path=f'/cms/cmsSearch/quick'
	key={'searching':account}
	respJson=requests_boss('POST',path,backType='json',env=env,data=key)
	# {'result': '1', 'message': 'success', 'data': {'list': [{'title': '472775 自动化测试后台开户', 'url': '/cms/cmsAccount/check?id=26264'}]}, 'now': '2021-09-01 17:46:13'}
	return respJson

def cmsAccount_check(checkid,backInfo='cif_no',env='uat'):
	path=f'/cms/cmsAccount/check?id={checkid}'
	soup=requests_boss('GET',path,backType='soup',env=env)
	ele=soup.find('div',text='账户持有人').parent.parent
	logging.info(f'{checkid} 对应账户持有人: {[ele.select_one(".a-left").text.strip()]}')
	if backInfo=='cif_no':
		result=ele.select_one('.a-right').text.strip()
		logging.info(f'cif_no查询结果: {[result]}')
		result=result.split()[0]
	return result

def getCardsID(account,env='uat'):
	# 查询账户的证件id
	respJson=cmsSearch_quick(account,env)
	cards=None
	if len(respJson['data']['list'])>0:
		checkid=respJson['data']['list'][0]['url'].split('=')[-1]
		cif_no=cmsAccount_check(checkid,env=env)

		path=f'/cms/cmsClientCertificate/refresh?cif_no={cif_no}'
		soup=requests_boss('GET',path,backType='soup',env=env)
		cards=[]
		for tr in soup.select_one('tbody').select('tr'):
			card_type=tr.select('td')[1].text.strip()
			card_id=tr.select('td')[2].text.strip()
			cards.append((card_type,card_id))
		logging.info(f'cards: {[cards]}')
		# [('香港居民身份证', 'R625079(2)'), ('中国居民身份证', '421022197904201518')]
	else:
		logging.info(f'查询账户{account}的checkid失败')
	return cards
################################################ 资金存入并审核 #########################################################################
def inmoney_CMS(account,currency,amount,env='test',check=1):
	# cms资金存入
	for i in range(5):
		userInfo=getInfoJSON(account,env)
		try:
			userInfo['data']
		except KeyError:
			return {"result":"0","msg":"casher/deposite/infoJSON 接口获取用户信息失败。",'userInfo':userInfo}
		if int(userInfo['result']) and userInfo['data']:
			break
		else:
			if i==4:
				return {"result":"0","msg":"casher/deposite/infoJSON 接口获取用户信息失败。",'userInfo':userInfo}
			else:
				time.sleep(1)
	
	bank_code_dict={'HKD':'238','USD':'238','CNY':'238'}
	bank_account_dict={'HKD':'20089188','USD':'20089199','CNY':'20510161'}
	key={
		"id":"",
		"accountid":account,
		"account_type":userInfo["data"]["AcctType"],
		"aecode":userInfo['data']['AECode'],
		"account_name":userInfo['data']['CName'],
		"account_name_en":userInfo['data']['Name'],
		"deposite_amount":amount,
		"currency":currency,
		"settlement_date":time.strftime('%Y-%m-%d'),
		"deposite_type":"1",
		"remark":"",
		"deposite_voucher_1":("4.png",open("testData/pic/1.png","rb"),"image/png"),
		"deposite_voucher_2":"",
		"deposite_voucher_3":"",
		"settlement_bank_account":"1",
		"deposite_bank_code":"238",
		"deposite_bank_account":str(randint(1000000000,9999999999)),
		"deposite_bank_account_name":userInfo['data']['CName'],
		"deposite_currency":currency,
		"third_deposits":"No",
		"bank_code":bank_code_dict[currency],
		"bank_account":bank_account_dict[currency],
		"bank_account_name":"CMB INTERNATIONAL SECURITIES LIMITED-CLIENT ACCOUNT",
		"bank_account_currency":currency,
		"fps_identification_code":"",
		"swift_code":"CMBCHKHH",
		"bank_address":"27/F, Three Exchange Square, 8 Connaught Place, Hong Kong",
	}
	path=f'/casher/deposite/save?id=&step_id=1987038'
	respJson=requests_boss('POST',path,backType='json',env=env,data=key)
	# logging.info(respJson)
	if type(respJson)==dict:
		try:
			data_id=respJson['data']['id']
		except:
			data_id=None
		result={'success':respJson['result'],'申请ID':data_id,'message':respJson['message'],'审核状态':'未审核'}
		if check:
			result_check=money_check(result['申请ID'],env=env,pathType='deposite')
			result['审核状态']=result_check['result']
	else:
		result={"result":"0","msg":f"{account} 存入 {amount}{currency} 异常: {respJson}"}
	logging.info(result)


################################################ 资金提取并审核 #########################################################################
def getInfoJSON(account,env='uat'):
	# 查询账户信息
	path=f'/casher/withdrawal/infoJSON?accountid={account}'
	respJson=requests_boss('GET',path,backType='json',env=env)
	return respJson

def getAvailableBalance(account,env='uat'):
	# 获取账户资金余额
	path=f'/casher/withdrawal/getAvailableBalance?accountid={account}'
	respJson=requests_boss('GET',path,backType='json',env=env)
	return respJson

def getSettlementAccount(account,currency,env='uat'):
	# 获取账户银行卡信息
	path=f'/casher/withdrawal/getSettlementAccount?accountid={account}&currency={currency}'
	respJson=requests_boss('GET',path,backType='json',env=env)
	return respJson

def getCompanyBankInfo(currency,bankCode,env='uat'):
	# 获取银行信息
	path=f'/casher/withdrawal/getCompanyBankInfo?currency={currency}&bankCode={bankCode}'
	respJson=requests_boss('GET',path,backType='json',env=env)
	return respJson

def withdrawalSave(account,currency,money=None,env='uat'):
	# 资金提取
	path=f'/casher/withdrawal/save?id=&step_id=1987046'
	userInfo=getInfoJSON(account,env)
	ableBalance=getAvailableBalance(account,env)
	logging.info(f'账户资金数据: {ableBalance}')
	bankCardInfo=getSettlementAccount(account,currency,env)
	bankInfo=getCompanyBankInfo(currency,bankCardInfo['data'][0]['bank_code'],env)
	data={
		'id':'',
		'accountid':account,
		'account_type':userInfo["data"]["AcctType"],
		'aecode':userInfo['data']['AECode'],
		'account_name':userInfo['data']['CName'],
		'account_name_en':userInfo['data']['Name'],
		'currency_hkd':ableBalance['data']['HKD'],
		'currency_usd':ableBalance['data']['USD'],
		'currency_cny':ableBalance['data']['CNY'],
		'current_balance_time':ableBalance['data']['current_balance_time'],
		'withdrawal_currency':currency,
		'withdrawal_amount':money or ableBalance['data'][currency].replace(',',''),
		'withdrawal_file_ro':'',
		'withdrawal_file_lcd':'',
		'remark':'',
		'settlement_card_id':bankCardInfo['data'][0]['card_id'],
		'settlement_bank_code':bankCardInfo['data'][0]['bank_code'],
		'settlement_bank_account':bankCardInfo['data'][0]['bank_account'],
		'settlement_bank_name':bankCardInfo['data'][0]['bank_name'],
		'settlement_bank_account_name':bankCardInfo['data'][0]['bank_account_name'],
		'settlement_bank_currency':currency,
		'settlement_swift_code':bankCardInfo['data'][0]['swift_code'],

		'company_bank_code':bankInfo['data']['bank_code'],
		'company_bank_account':bankInfo['data']['bank_account'],
		'company_bank_account_name':bankInfo['data']['bank_account_name'],
	}
	logging.info(f'资金提取请求数据: {data}')
	respJson=requests_boss('POST',path,backType='json',env=env,data=data)
	return respJson

def getApproveStatus(approveId,env='uat',pathType='withdrawal',keyword='业务状态'):
	# 查询资金存入/提取业务状态
	path=f'/casher/{pathType}/approve?id={approveId}'
	soup=requests_boss('GET',path,backType='soup',env=env)
	status=soup.find('div',text=keyword).next_sibling.next_sibling.text.strip()
	return status

def money_check(approveIdList,env='uat',to_step_id='pass',pathType='withdrawal',bigMoney=0):
	# 审核通过
	if isinstance(approveIdList,str):approveIdList=[approveIdList]
	result={"success":True,"result":[]}
	stepId_dict={
		'deposite':{'RM修改':'1987038','结算审批':'1987040'},
		'withdrawal':{'RM修改':'1987046','RO审批':'1987220','LCD审批':'1987224','结算审批':'1987052'},
	}
	for approveId in approveIdList:
		if bigMoney:limitAmountInfo(approveId,env)
		n=1
		while n:
			status=getApproveStatus(approveId,env,pathType)
			approve_note='Stopped By AppAutoTest' if to_step_id=='-2' else f'{status}通过'
			key={'current_step_id':stepId_dict[pathType][status],'to_step_id':to_step_id,'approve_note':approve_note}
			if status=='结算审批' or to_step_id=='-2':n=0
			elif status not in ['RM修改','RO审批','LCD审批']:
				result["result"].append(f'{approveId}审核失败,该申请ID状态异常: {[status]}')
				break
			path=f'/casher/{pathType}/approve?id={approveId}'
			respJson=requests_boss('POST',path,backType='json',env=env,data=key)
			try:
				result["result"].append(f'{approveId} {status} 审核结果:{respJson}')
			except simplejson.errors.JSONDecodeError:
				result["result"].append(f'{approveId} {status} 审核异常: {resp.text}')
				result["success"]=False
	return result

def limitAmountInfo(approveId,env='uat'):
	# 大额资金提取背景说明
	path=f'/casher/withdrawal/limitAmountInfo?id={approveId}'
	business_no=getApproveStatus(approveId,env=env,pathType='withdrawal',keyword='业务编号')
	data={
		'id':approveId,
		'business_no':business_no,
		'withdraw_background':'Others',
		'withdraw_background_other':'byAutotest',
		'withdraw_background_confirm[]':'Yes',
		'withdraw_reason':'byAutotest',
	}
	respJson=requests_boss('POST',path,backType='json',env=env,data=data)
	logging.info(f'大额资金提取背景说明: {respJson}')

##################### 终止账户所有资金提取 ##########################################
def getCasherWithdrawal(account,env='uat'):
	# 基账户号查询资金申请列表
	key={'step_id':'All','aecode':'','accountid':account,'page':1,'limit':2000}
	path='/casher/withdrawal/list'
	soup=requests_boss('GET',path,backType='soup',env=env,params=key)
	approveIdList=[]
	for tr in soup.select('tr'):
		try:
			status=tr.select_one('.step_id').text.strip()
			if status!='完成':
				approveIdList.append([tr.select('td')[-1].select_one('a')['href'].split('=')[-1],status,tr.select('td')[4].text.strip(),tr.select('td')[6].text.strip(),tr.select('td')[8].text.strip(),tr.select('td')[-2].text.strip()])
				# approveIdList.append(tr.select('td')[-1].select_one('a')['href'])
		except (TypeError,IndexError,AttributeError):
			pass
	return approveIdList

def stopAllApprove(account,env='uat'):
	approveIdList=getCasherWithdrawal(account,env)
	for approveId_info in approveIdList:
		if approveId_info[1] in ['已终止','完成']:
			logging.info(f'{approveId_info[0]} {approveId_info[1]}')
		else:
			result=money_check(approveId_info[0],env,to_step_id='-2')
			logging.info(f'{approveId_info[0]} {result}')

###################### 切换开户渠道 ####################################################
def changeChannel(channel='TTL',env='uat'):
	path=f'/master/masterSetting/edit'
	data={
		'id':'14',
		'key_code':'CHANNEL',
		'key_value':channel.upper(),
		'remark':'证券系统渠道(ABC/TTL)',
	}
	respJson=requests_boss('POST',path,backType='json',env=env,data=data)
	logging.info(f'{env} 切换开户渠道为 {channel} 结果: {respJson}')

##################################################################################################################
def getSession_key(env='test',link_id='516'):
	path=f'/frame/body/load?link_id={link_id}'
	soup=requests_boss('GET',path,backType='soup',env=env)
	return soup.select_one('iframe')['src']

def addPfund(currency,env='test'):
	# 新增私募基金产品
	path=None
	# session_key=getSession_key(env).split('?')[1]
	# url=f'http://{env}-boss-combine.****.*****/admin/pFundProduct/save?{session_key}'
	url=f'http://pmo.{env}-boss.****.*****/pmo-gateway/auth/fundPrivate/add'
	fundNameCn=f'基金名称{time.strftime("%m-%d %H-%M-%S")}'
	_head={
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
		'Cookie':'',
		'Content-Type':'application/json;charset=UTF-8',
		'Connection':'close',
		'X-Requested-With':'XMLHttpRequest',
		'k8sHost':'http://pmo-product-info-service-v1.tradingmo.svc.cluster.local:8080/pmo_product_info_service',
		'privilegeCode': 'pfund_manage:modify',
	}
	data={
		'afterLockPeriodRedRate':"1",
		'commission':"1",
		'commissionDeductType':"1",
		'createdBy':"1060",
		'currency':currency,
		'cutOffTime':"16:00:32",
		'establishDate':"2022-07-26",
		'fundClass':"私募股权基金",
		'fundManager':"AutoTest",
		'fundNameCn':fundNameCn,
		'fundNameEn':f'Fund Name {time.strftime("%m-%d %H-%M-%S")}',
		'fundScale':"500000000",
		'fundScaleDate':"2022-07-26",
		'hardLockPeriod':"0",
		'investFixedYears':"不超过1年",
		'investOrientation':"投资方向",
		'investTarget':"保本为主 - Capital Preservation",
		'isComplexFund':"否",
		'isHaveDerivative':"否",
		'isHighYield':"否",
		'isProfessionalInvestor':"否",
		'isRedemptionPermit':"是",
		'isSfc':"是",
		'isSpecialAccSubscribe':"否",
		'isSubscribePermit':"是",
		'manageFee':"2",
		'maturityDate':"2029-07-26",
		'miniRenewalAmount':"10",
		'miniSubAmount':"10",
		'numberOfShareDecimal':"2",
		'orgCode':"201701",
		'performanceFee':"1",
		'ratingEffectiveDate':"2022-07-26",
		'redCutOffDate':"2122-07-26",
		'redFeeDeductType':"2",
		'redOpenSeason':"2022-07-26",
		'redValuationDay':"2022-07-26",
		'riskRating':"1.低风险 - Low",
		'rpqClass':"Others其它",
		'softLockPeriod':"0",
		'softLockPeriodRedRate':"2",
		'subCutOffDate':"2022-07-26",#认购截单日
		'subOpenSeason':"2022-07-26",
		'subValuationDay':"2022-07-26",
		'targetCustomer':"自拓客户",
	}
	time.sleep(1)
	respJson=requests_boss('POST',path,url,header=_head,backType='json',env=env,json=data)
	logging.info(f'{env} 新增私募基金产品 {fundNameCn} 结果: {respJson}')
	return fundNameCn

def queryPfundCode(pFundName,env='test'):
	# 根据私募基金名称查询私募基金的productcode
	path=None
	# session_key=getSession_key(env).split('?')[1]
	url=f'http://pmo.{env}-boss.****.*****/pmo-gateway/auth/fundPrivate/pageQuery'
	_head={
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
		'Cookie':'',
		'Content-Type':'application/json;charset=UTF-8',
		'Connection':'close',
		'X-Requested-With':'XMLHttpRequest',
		'k8sHost':'http://pmo-product-info-service-v1.tradingmo.svc.cluster.local:8080/pmo_product_info_service',
		'privilegeCode': 'pfund_manage:view',
	}
	data={
		'fundName':pFundName,
		'page':1,
		'pageSize':10
	}
	respJson=requests_boss('POST',path,url,header=_head,backType='json',env=env,json=data)
	logging.info(f'{env} 查询私募基金产品 {pFundName} 结果: {respJson}')
	return respJson['result']['pfundProductList'][0]['prdCode']

def getPower(accountid,prdCode,types='bondOrder',env='test'):
	# 查询购买力
	session_key=getSession_key(env).split('?')[1]
	currency=prdCode[-3:]
	url=f'http://{env}-boss-combine.****.*****/admin/{types}/placeOrder?side=1&accountid={accountid}&productCode={prdCode}&currency={currency}&{session_key}'
	respJson=requests_boss('GET',None,url,backType='json',env=env)
	logging.info(f'{env} 查询{types}购买力 {currency} 结果: {respJson}')
	return respJson['data']['buyPower']['powerAmount']

#############################################################################################
def add_structure(currency,env='uat'):
	# 新增结构化产品
	path=None
	url_add=f'http://pmo.{env}-boss.****.*****/pmo-gateway/auth/structure/add'
	url_update=f'http://pmo.{env}-boss.****.*****/pmo-gateway/auth/structure/update'
	structureName=f'结构化名称{time.strftime("%m-%d %H-%M-%S")}'
	_head={
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
		'Content-Type':'application/json;charset=UTF-8',
		'Connection':'close',
		'X-Requested-With':'XMLHttpRequest',
		'k8sHost':'http://pmo-product-info-service-v1.tradingmo.svc.cluster.local:8080/pmo_product_info_service',
		'privilegeCode': 'structuralization_list:modify',
	}
	data1={
		'coupon': None,
		'dividendCoupon': None,
		'dividendFrequency': None,
		'downAdjust': None,
		'highCoupon': None,
		'investmentCurrency': currency,
		'investmentHorizon': "",
		'issueDate': "2022-07-28",
		'issuer': "Autotest",
		'knockInPrice': None,
		'knockOutPrice': None,
		'linkTarget': "",
		'lockPeriod': "",
		'lockPeriodNum': None,
		'lowCoupon': None,
		'observeDate': None,
		'observeFrequency': None,
		'participationRate': None,
		'productName': structureName,
		'productNature': "Structured Note",
		'productType': "ELN",
		'risk': "",
		'paperPrice': "1.3",
		'settlementDate': "2022-07-29",
		'status': "待上架",
		'targetType': "Equity",
		'sheetNumber': "1",
	}
	respJson=requests_boss('POST',path,url_add,header=_head,backType='json',env=env,json=data1)
	logging.info(f'{env} 新增结构化产品 {structureName} 结果: {respJson}')
	productCode=respJson['result']
	data2={
		'commission': None,
		'commissionDeductType': "内扣",
		'custodianFee': None,
		'expirationDate': "16:08:03",
		'isGroupBuying': "是",
		'maximumInvestmentAmount': None,
		'minimumInvestmentAmount': None,
		'productCode': productCode,
		'renewalAmount': None,
		'sheetNumber': "2",
	}
	data3={
		'investFixedYears': "不超过1年",
		'investTarget': "保本为主",
		'isBuyRestrict': "否",
		'isComplexFund': "否",
		'isCsrcEndorsement': "是",
		'isHaveDerivative': "否",
		'isProvideInvestmentSubscribed': "否",
		'isSaleRestrict': "否",
		'productCode': productCode,
		'rateDate': "2022-07-27",
		'riskRating': "1.低风险",
		'rpqType': "d)保本结构性产品;例如：结构性存款",
		'sheetNumber': "3",
	}
	for d in [data2,data3]:
		respJson=requests_boss('POST',path,url_update,header=_head,backType='json',env=env,json=d)
		logging.info(f'{env} 新增结构化产品 {structureName} 结果: {respJson}')
	batchSend(productCode,env)
	return productCode

def batchSend(productCode,env='uat'):
	# 推送结构产品到ttl
	path=None
	url=f'http://pmo.{env}-boss.****.*****/pmo-gateway/auth/structure/batchSend'
	_head={
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
		'Content-Type':'application/json;charset=UTF-8',
		'Connection':'close',
		'X-Requested-With':'XMLHttpRequest',
		'k8sHost':'http://pmo-product-info-service-v1.tradingmo.svc.cluster.local:8080/pmo_product_info_service',
		'privilegeCode': 'structuralization_list_send:modify',
	}
	data={"prdCodeList":productCode}
	respJson=requests_boss('POST',path,url,header=_head,backType='json',env=env,json=data)
	logging.info(f'{env} 推送架构华产品 {productCode} 结果: {respJson}')
	# return respJson['result']['pfundProductList'][0]['prdCode']




if __name__ == '__main__':
	# print(('1v2d84xegcw9jny6o0kf@9rfl6tw7bymjcnv.com','uat'))
	addPfund('USD')
