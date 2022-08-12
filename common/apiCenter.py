import requests,time,logging,sys,traceback,re,simplejson
from jsonpath import jsonpath
# from .dbOperation import excuteSQL
from .system_boss import getSMScode,getCardsID
from .tools import encode_md5,encryption
requests.packages.urllib3.disable_warnings()

# app 相关接口
head={
	'Content-Type':'application/json;charset=UTF-8',
	'Accept':'application/json',
	'Connection':'close',
	'X-Requested-With': 'XMLHttpRequest'
}

head_urlencode={
	'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
	'Connection':'close',
}

ttl_app_domain={
	'test':'http://trade-test.****.*****',
	'uat':'http://trade-uat.****.*****',
}

##################################################################################################################
def addHOld_ttl(account,stockCode,stockNum,market,DW='D',env='uat'):
	# ttl 加持仓 currency: ['HKD','USD','CNY']
	global head
	marketID_dict={'HKG':'HKEX','USA':'USEX','SHA':'MAMK','SZA':'SZMK','FUND':'FUND','BOND':'BOND','SPMK':'SPMK'}
	if env in ['test','dev']:
		url='http://172.0.0.0:8089/mobile/services/v0/instrumentDW'
	elif env=='uat':
		url='http://192.0.0.0:8089/mobile/services/v0/instrumentDW'
	data={
		"clientID":account,
		"tranType":DW,
		"marketID":marketID_dict[market],
		"instrumentID":stockCode,
		"settleMethod":DW,
		"qty":stockNum,
		"sessionID":"sessionID",
		"waiveAllFees":"Y"
	}
	resp=requests.post(url,headers=head,json=data)
	# respJson={'result':resp.text}
	try:
		respJson=resp.json()
	except simplejson.errors.JSONDecodeError:
		logging.error(f'返回数据异常: {resp.text}')
		respJson={'success':0,'errorMsg':resp.text}
	logging.info(f"{account}加持仓{stockCode} {stockNum}股 结果: {resp.text}")
	return respJson

def add_ttlhuidu(account,env='test'):
	global head
	url=f'http://trade-{env}.****.*****/cif/public/gray/addBatch'
	data={
		"accounts":"",
		"isNow":True,
		"traceLogId":f"fromAutotest{time.time()}"
	}
	if isinstance(account,str):
		data['accounts']=[account]
	elif isinstance(account,list):
		data['accounts']=account
	resp=requests.post(url,headers=head,json=data)
	respJson=resp.json()
	if respJson['success']:
		logging.info(f'{account} 添加{env}环境ttl灰度名单成功')
		return 1
	else:
		logging.info(f'{account} 添加{env}环境ttl灰度名单失败: {respJson}')
		return 0

def login_acc(uname,pword,env='test',ttl=1):
	global head
	head['User-Agent']='zyapp/2.2.1.36591 (HONOR COLAL10; Android 9) uuid/VBJDU19510007442 channel/Atest1 redgreensetting/red language/zhCN versionCode/33562625'
	if ttl:
		url=f'http://trade-{env}.****.*****/auth-center/public/login/accountLogin'
		data={"traceLogId":f"fromAutotest{time.time()}","accountNo":uname,"tradePwd":pword}
		# timestamp,signature=encryption(data)
		# head["TIMESTAMP"]=timestamp
		# head["SIGNATURE"]=signature
		# head["headerTraceLog"]="and"+timestamp
		resp=requests.post(url,headers=head,json=data)
		# del head["SIGNATURE"]
		# del head["TIMESTAMP"]
		# del head["headerTraceLog"]
	else:
		head['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
		url=f'http://{env}-app.****.*****/app/user/loginexchange'
		data={'account':uname,'password':pword}
		resp=requests.post(url,headers=head,data=data,verify=False)
	respJson=resp.json()
	# print(f'{uname} debug: {respJson}')
	if respJson:
		try:
			sessionDic={
				# 'token':jsonpath(respJson,['$..loginToken','$..token'])[0],
				'token':(jsonpath(respJson,'$..loginToken') or jsonpath(respJson,'$..token'))[0],
				'sessionId':(jsonpath(respJson,'$..session') or jsonpath(respJson,'$..sessionid'))[0],
				'acctType':'MRGN' if 'M' in uname else 'CASH',
				'aeCode':(jsonpath(respJson,'$..aeCode') or jsonpath(respJson,'$..aecode'))[0],
				'marginMax':(jsonpath(respJson,'$..marginMax') or jsonpath(respJson,'$..margin_max'))[0],
				'accountId':uname,
				'accountName':(jsonpath(respJson,'$..acctName') or jsonpath(respJson,'$..account_name'))[0],# 中文名
				'operatorNo':(jsonpath(respJson,'$..operatorNo') or jsonpath(respJson,'$..user_id'))[0],
				'phone':jsonpath(respJson,'$..phone')[0],
			}
			if ttl:sessionDic['enName']=getBindBankListByAccountId(sessionDic,env)
			return sessionDic
		except Exception as err:
			logging.info(f'{uname} 登录失败: {respJson}')
			raise err
	else:
		raise Exception(f'{uname}登录失败: {respJson}')

def getBindBankListByAccountId(sessionDic,env='test'):
	global head
	url=f'http://trade-{env}.****.*****/gateway/casher/getBindBankListByAccountId'
	data={
		"accountid":sessionDic['accountId'],
		"accountNo":sessionDic['accountId'],
		"accountId":sessionDic['accountId'],
		"operatorNo":sessionDic['operatorNo'],
		"sessionId":sessionDic['sessionId'],
		"session":sessionDic['sessionId'],
		"loginToken":sessionDic['token'],
		"token":sessionDic['token'],
		"acctType":sessionDic['acctType'],
		"marginMax":sessionDic['marginMax'],
		"aecode":sessionDic['aeCode'],
		"isProspect":0,
		"currency":"USD",
		"traceLogId":f"fromAutotest{time.time()}"
	}
	resp=requests.post(url,headers=head,json=data)
	respJson=resp.json()
	try:
		return respJson['result']['client_bank_account_name']
	except:
		raise Exception(f'{sessionDic} 返回数据异常: {respJson}')

def submitDeposite(sessionDic,currency,env='test'):
	# ttl 资金存入 currency: ['HKD','USD','CNY']
	global head
	bankCodeDic={'HKD':'44700867093','USD':'44700867131','CNY':'44700867107'}
	url=f'http://trade-{env}.****.*****/gateway/casher/submitDeposite'
	# sessionDic=login_ttl(uname,pword,env)
	data={
		"traceLogId":f"fromAutotest{time.time()}",
		"org_code":"CMBIS",
		"company_bank_account_name":"CMB INTL S L - C A/C",
		"company_bank_name":"渣打银行（香港）有限公司",
		"company_bank_code":"003",
		"company_bank_account":bankCodeDic[currency],
		"txn_way":1,
		"apply_amount":"100000000",
		"client_bank_account":"333365585266",
		"client_bank_name":"渣打银行（香港）有限公司",
		"client_bank_code":"003",
		"isProspect":0,
		"org_id":"56",
		"certify_data_01":"202103/depositnode_918730_202103291438385803.jpg",
		"certify_data_02":"",

		"currency":currency,
		"client_bank_account_name":sessionDic['enName'],

		"accountid":sessionDic['accountId'],
		"accountNo":sessionDic['accountId'],
		"accountId":sessionDic['accountId'],
		"operatorNo":sessionDic['operatorNo'],
		"sessionId":sessionDic['sessionId'],
		"session":sessionDic['sessionId'],
		"loginToken":sessionDic['token'],
		"token":sessionDic['token'],
		"acctType":sessionDic['acctType'],
		"marginMax":sessionDic['marginMax'],
		"aecode":sessionDic['aeCode'],
	}
	resp=requests.post(url,headers=head,json=data)
	respJson=resp.json()
	uname=sessionDic['accountId']
	if respJson['success']:
		logging.info(f'{uname} {env}环境存入 {currency} 成功')
		return sessionDic
	else:
		logging.info(f'{uname} {env}环境存入 {currency} 失败: {respJson}')
		return 0

def resetAccountPwdSendCode(account,env='uat'):
	global head
	url=f'http://trade-{env}.****.*****/gateway/account/resetAccountPwdSendCode'
	cerNo=getCardsID(account,env)[0][1]
	data={"traceLogId":f"fromAutotest{time.time()}","accountNo":account,"cerNo":cerNo,"codeType":"normal","json":True,"lang":"cn","signature":True}
	timestamp,signature=encryption(data,'H5')
	head["timestamp"]=timestamp
	head["signature"]=signature
	resp=requests.post(url,headers=head,json=data)
	del head["signature"]
	del head["timestamp"]

	respJson=resp.json()
	logging.info(respJson)

def unlockAcc(account,env='uat'):
	resetAccountPwdSendCode(account,env)
	global head
	url=f'http://trade-{env}.****.*****/gateway/account/unlock'
	data={
		"code":"8888",
		"accountNo":account,
		"traceLogId":f"fromAutotest{time.time()}",
		"lang":"cn",
		"signature":True,
		"json":True,
	}

	timestamp,signature=encryption(data,'H5')
	head["timestamp"]=timestamp
	head["signature"]=signature
	resp=requests.post(url,headers=head,json=data)
	del head["signature"]
	del head["timestamp"]

	respJson=resp.json()
	logging.info(respJson)

def cancelFinance(Maccount,pword,env='uat',ttl=1):
	# 取消融资额度申请
	url=f'http://trade-{env}.****.*****/gateway/business/cancelFinanceQuotaLimitApply'
	sessionDic=login_acc(Maccount,pword,env,ttl)
	data={
		"traceLogId":f"fromAutotest{time.time()}",
		"token":sessionDic['token'],
		"operatorNo":sessionDic['operatorNo'],
		"sessionId":sessionDic['sessionId'],
		"accountId":Maccount,
		"acctType":sessionDic['acctType'],
		"aecode":sessionDic['aeCode'],
		"marginMax":sessionDic['marginMax'],
		"marginAccount":Maccount,
		"json":True,
		"lang":"cn"
	}
	resp=requests.post(url,headers=head,json=data)
	respJson=resp.json()
	logging.info(f'取消融资额度申请结果: {respJson}')

######################################### 行情卡相关 ################################################################
def cardOperate(sessionDic,env='uat'):
	url=f"http://trade-{env}.****.*****/gateway/quote/cardOperate"
	data={
		"token":sessionDic['token'],
		"sessionId":sessionDic['sessionId'],
		"accountId":sessionDic['accountId'],
		"acctType":sessionDic['acctType'],
		"aecode":sessionDic['aeCode'],
		# "marginMax":sessionDic['marginMax'],
		"operatorNo":sessionDic['operatorNo'],
		# "operateCode":"RENEWAL",
		"operateCode":"UPGRADE",
		"market":"HK",
		"productId":"2",
		"planNum":2,
		"mobile":sessionDic['phone'],
		"accountAmount":"10000000",
		"payAmount":1200
	}
	# print(data)
	logging.info(f'{sessionDic["accountId"]} 购买港股行情卡')
	resp=requests.post(url,headers=head,json=data)
	logging.info(f'购买结果: {resp.text}')


def signAgreement(sessionDic,env='uat'):
	url=f"http://trade-{env}.****.*****/gateway/operator/signAgreement"
	data={
		"agreementType":"US_STOCK_UPGRADE",
		"operatorNo":sessionDic['operatorNo'],
		"token":sessionDic['token'],
		"traceLogId":f"fromAUTOTEST{time.time()}"
	}
	logging.info(f'{sessionDic["accountId"]} 美股行情卡免费升级')
	resp=requests.post(url,headers=head,json=data)
	logging.info(f'购买结果: {resp.text}')
	

##################################################################################################################

def resetpwd_abc(uname,newpwd,env='test'):
	url=f"http://{env}-app.****.*****/app/exchange/resetPassword"
	try:
		card_id=get_cardID(uname,env)[0][0]
	except TypeError:
		card_id=None
	if card_id:
		head={
			'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
			'Connection':'close',
		}
		result=resetCode(uname,card_id,env,head)
		if result['result']!='1':return result
		data={
			"accountid":uname,
			"card_id":card_id,
			"sms_code":"8888",
			"password":newpwd,
			"callType":"normal",
		}
		resp=requests.post(url,headers=head,data=data)
		try:
			respJson=resp.json()
		except simplejson.errors.JSONDecodeError:
			respJson={"success":False,"msg":"执行失败","responseText":resp.text}
	else:
		msg=f'从数据库查询 {env} 环境账户 {uname} 的card_id失败，请检查 OctOSTP_Front.dbo.ClntPasswords 及 IBFront.dbo.ClntStaticInfo 表内是否有 {uname} 相关数据。'
		respJson={"success":False,"msg":msg}
	return respJson

def resetCode(uname,card_id,env,head):
	url=f"http://{env}-app.****.*****/app/exchange/resetCode"
	data={"accountid":uname,"card_id":card_id,"callType":"normal",}
	resp=requests.post(url,headers=head,data=data)
	return resp.json()

def get_cardID(uname,env='test'):
	check_sql=f"SELECT Residentid FROM IBFront.dbo.ClntStaticInfo WHERE ClntCode='{uname}'"
	result=excuteSQL(check_sql,dbType='sqlserver',env=env)
	return result

def resetpwd_ttl(uname,newpwd,env='test'):
	newpwd=encode_md5(f'{uname}_{newpwd}').upper()
	if env=='test':
		url='http://172.0.0.0:8089/mobile/services/v0/updatePassword'
	elif env=='uat':
		url='http://192.0.0.0:8089/mobile/services/v0/updatePassword'
	head={
		'Content-Type':'application/json;charset=UTF-8',
		'X-Request-ID':'00000000001',
		'Accept':'application/json',
		'Connection':'close',
	}
	data={
		"channelID":"INT",
		"clientID":uname,
		"newPassword":newpwd,
		"encrypt":"N"
	}
	resp=requests.post(url,headers=head,json=data)
	respJson=resp.json()
	if respJson['returnCode']=='0000':
		return {'result':'1'}
	else:
		# print(f'{uname} 重置密码失败: {respJson}')
		return {'result':'0','msg':respJson}

def resetpwd(uname,newpwd,env='test',ttl=0):
	if ttl:
		return resetpwd_ttl(uname,newpwd,env)
	else:
		return resetpwd_abc(uname,newpwd,env)

##################################################################################################################
def setPwdTel(args,newPwd):
	#手机号第一次登录 设置密码
	for i in range(30):
		token,reason=login_telSMS_interface(args)
		if token:
			key={
				'new_password':newPwd,
				'token':token,
			}
			resp=requests.post(f'http://{args.env}-app.****.*****/app/user/completePassword',headers=head_urlencode,data=key,verify=False)
			respJson=resp.json()
			if respJson['result']=='1':
				return 1,0
			else:
				return 0,respJson
		else:
			if i==29 or '过于频繁' not in str(reason):return 0,reason
			else:time.sleep(1)

def login_telSMS_interface(args):
	#接口方式 手机号+验证码登录
	status,reason=sendSMS(args)
	time.sleep(3)
	vcode=getSMScode(args.tel,args.env,n=4)
	if status:
		key={
			'mobile':args.tel,
			'mobcountry':args.areaCode,
			'vcode':vcode,
			'type':'vcode',
		}
		resp=requests.post(f'http://{args.env}-app.****.*****/app/user/login',headers=head_urlencode,data=key,verify=False)
		respJson=resp.json()
		if respJson['result']=='1':
			return respJson['data']['token'],0
		else:
			return 0,respJson
	else:
		return 0,reason

def sendSMS(args):
	key={
		'mobile':args.tel,
		'mobcountry':args.areaCode,
	}
	resp=requests.post(f'http://{args.env}-app.****.*****/app/user/applyAuthCode',headers=head_urlencode,data=key,verify=False)
	respJson=resp.json()
	if respJson['result']=='1':
		return 1,0
	else:
		return 0,f'手机号登录时发送验证码失败： {respJson}'
##################################################################################################################
def w8InfoSubmit(sessionDic,w8table_no=None,env='test'):
	global head_urlencode
	url=f'http://trade-{env}.****.*****/app/exchange/w8InfoSubmit'
	if w8table_no:
		data={
			'submit_type':'submit',
			"w8table_no":w8table_no,
			"sign_img":'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEkAAABVCAYAAAAFZ8k8AAAEUElEQVR4Xu2bWegPURTHf39L5MG+ZCuy5AGJbAl/EgmhLH9L8iTkxYMsZcmWLSUp8iSUpRDyYI1seVBCWVMSsnuQffme/v/RdLszc37zvzNz5vc7t0795t4zc8/5/M69c7epKGiKJFARqaEKBYXECAKFpJAYBBgqGkkKiUGAoaKRpJAYBBgqGkkKiUGAoaKRpJAYBBgq5RBJG8BhOKQu5BZkLeQ9g81/lVKH9BqetjGAXMZ1pUKqJnAKMj4ARjfkP+GCKtVI2g8As0Mg9EPZ7XKGdAzOT44A0Arl78oV0kw4fjDC+aMon8YFRHql1NxWwB96kwWlvyi4CBlVDKBSgnQIzkwPcf4LyvpCHhULqFQgjaiJkCD/v6KgCnIyDqBSgDQATpyFNAkAcAn5YyA/4wLKO6SJcGBfCKB7KOtVGzjevXntuAnQiRAANO3oAvlcrpAawfHHkHYBAI5EdOJFc8tjJJ2Gl+MCPN2N/AVFU4i4IW+QjsOfSQE+3UF+H9eA8tZxP4fBHQMgPKgB9L2cIe2B8/MCAOwNKXPCLA/NbQI8DRoI0hBgrhMSIQ+RDqknbL8KsQ0WnyK/a9KApPdJ/WHgeUhjC4g3yKM1oRflDulTQARdR/5ISCKdtA261OZGIAZbDKZBZCXkZRoR5NUhEdIwGEeL9Wb6gwwaB91NE5DEPqkDjHoGqWcBQSuOYevWibGTFkk34Okgi7e0HEJLHpkkSZCugMBQCwUaSM7PhE5NpVIgdYY9NO4x7fmIvOZZApLSJ9H281tIMwPGB1y3yBqQFEiHYYhti2cZ8jcrpEJhOyAstoBYhbx1EgBJiCTqc5oaMGig2F4KoKwh0ejZnKDS1jNtQYtKWb3daO51wSBBO6xLIVtFEYIxWUH6hrobGDA24Xq5NEBZNTc6sDDFgPEQ1z0kAsoC0lhUesaA8QvX9aUCygKSbTF/CQzZppCqCeyCLDRg0Buuu2RAaUZSJ1RGx178zUrk6972h6X1drMtgayEQeulR1FakbTR8mqng59z8gAoLUg0w2/pA5KbZubZnHRzoz2zIUbE0F7a/bxEUdKR1BoVvILU8QGhs40z8gQoaUg0m2/rAyJilTHOH5RUc6NFNFpM89Jv/KCPYK7FMTLre5KARPv29OFLQ59zNBUJOniVNYPI+pOAdAC1zvLVTJuJvSMtEazgGtIa+Lra8JcApb7r6pK5a0jmBDY3o+owqC4h0anXqb7K6HiM+UGeyz84tWe5gkRr1TSj9xKdn6Y89udSqXkcoyJXkG6i7oG++mmteksMe0Te4gISncynE/peOocfo0V6G9MoF5B+oG5vnSi3o+okO27/aiNtCdFuh4it6ZhBY72ttpHk36YmYItcGiflWbWFRH7shNDn4zukOOXaDheQXNsk7nkKifGXKCSFxCDAUNFIUkgMAgwVjSSFxCDAUNFIUkgMAgwVjSSFxCDAUNFIUkgMAgyVfzq8g1bTHniDAAAAAElFTkSuQmCC',
			'accountid':sessionDic['accountId'],
			'sessionid':sessionDic['sessionId'],
			'acctype':sessionDic['acctType'],
			'aecode':sessionDic['aeCode'],
			'margin_max':sessionDic['marginMax'],
			'token':sessionDic['token'],
		}
	else:
		data={
			'country':'CHN',
			'residence_country':'CHN',
			'residence_country_same':'1',
			'mail_address_country':'CHN',
			'mail_address_country_same':'1',
			'birthday':'1984-06-01',
			'ssn_itin':'',
			'foreign_tax_num':'',
			'address':'TTL',
			'mail_address':'xiang gang',
			'mail_address_same':'0',
			'passport_img':'',
			'passport_name':'',
			'passport_number':'',
			'passport_valid_date':'',
			'submit_type':'save',
			'name':sessionDic['enName'],
			'accountid':sessionDic['accountId'],
			'sessionid':sessionDic['sessionId'],
			'acctype':sessionDic['acctType'],
			'aecode':sessionDic['aeCode'],
			'margin_max':sessionDic['marginMax'],
			'token':sessionDic['token'],
		}
	resp=requests.post(url,headers=head_urlencode,data=data)
	respJson=resp.json()
	return respJson

def createW8Pdf(sessionDic,w8table_no,env='test'):
	global head_urlencode
	url=f'http://trade-{env}.****.*****/app/exchange/createW8Pdf'
	data={
		'accountid':sessionDic['accountId'],
		'sessionid':sessionDic['sessionId'],
		'acctype':sessionDic['acctType'],
		'aecode':sessionDic['aeCode'],
		'margin_max':sessionDic['marginMax'],
		'token':sessionDic['token'],
		'w8table_no':w8table_no,
	}
	resp=requests.post(url,headers=head_urlencode,data=data)
	respJson=resp.json()
	return int(respJson['result'])

def w8Submit(sessionDic,env='test'):
	respJson=w8InfoSubmit(sessionDic,w8table_no=None,env=env)
	logging.info(f"{sessionDic['accountId']} {respJson['message']}")
	w8table_no=respJson['data']['w8table_no']
	result=createW8Pdf(sessionDic,w8table_no,env=env)
	if result:logging.info(f"{sessionDic['accountId']} createW8Pdf 成功")
	respJson=w8InfoSubmit(sessionDic,w8table_no=w8table_no,env=env)
	logging.info(f"{sessionDic['accountId']} {respJson['message']}")

##################################################################################################################
def openMarket(sessionDic,env='test'):
	global head_urlencode
	url=f'http://trade-{env}.****.*****/app/exchange/openMarket'
	data={
		'accountid':sessionDic['accountId'],
		'sessionid':sessionDic['sessionId'],
		'acctype':sessionDic['acctType'],
		'aecode':sessionDic['aeCode'],
		'margin_max':sessionDic['marginMax'],
		'token':sessionDic['token'],
		'mk_hk':'0',
		'mk_hs':'1',
		'mk_hsb':'1',
		'mk_otc':'1',
		'mk_us':'1',
	}
	resp=requests.post(url,headers=head_urlencode,data=data)
	respJson=resp.json()
	logging.info(f"{sessionDic['accountId']} {respJson['message']}")
##################################################################################################################
def getVersJson():
	head={
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
		'Connection':'close',
	}
	for i in range(3):
		resp=requests.post('https://labor.****.*****',headers=head)
		try:
			versJson=resp.json()
			return versJson
		except Exception as err:
			logging.error(traceback.format_exc())
			logging.info('2 秒后重试...')
			time.sleep(2)

def checkNew(cusVer=None):
	return '100.100.100.100'
	versJson=getVersJson()
	if cusVer:
		for appInfo in versJson['android']:
			try:
				appVer=re.findall(r'\d\.\d\.\d+\.\d+',appInfo['version'])[0]
			except IndexError:
				continue
			if appVer==cusVer:return appInfo
		print(f'无法从 https://labor.****.***** 找到版本 {cusVer} 的相关信息')
		sys.exit()
	else:
		from .tools import maxVersion
		newerVer='0.0.0'
		for appInfo in versJson['android']:
			try:
				appVer=re.findall(r'\d\.\d\.\d+\.\d+',appInfo['version'])[0]
			except IndexError:
				continue
			newerVer=maxVersion(newerVer,appVer)
		return newerVer

def downloadApp(appinfo):
	logging.info(f'开始下载 {appinfo["version"]} APP {appinfo["fullname"]}')
	savePath='testData/apk'
	cmd=f'aria2c -d "{savePath}" -o {appinfo["fullname"]} https://labor.****.*****{appinfo["filelink"]}'
	import os
	os.system(cmd)

######################################### 新股IPO相关 ################################################################
def orderSubmitIPO(sessionDic,env='uat'):
	# 新股认购 普通人狗
	url=f"http://trade-{env}.****.*****/gateway/ipo/orderSubmit"
	data={
		"sessionId":sessionDic['sessionId'],
		"accountId":sessionDic['accountId'],
		"accountName":sessionDic['accountName'],
		"acctType":sessionDic['acctType'],
		"aeCode":sessionDic['aeCode'],
		"marginMax":sessionDic['marginMax'],
		"token":sessionDic['token'],
		"tokenId":"",

		"department":"PWM",
		"subscribeType":"CASH",
		"stockCode":"07028",
		"stockName":"天翼科技（自动化专用）",
		"applySubscribeNum":"10000000",
		"subscribePrice":"199995246.00",
		"currencyUnit":"HKD",
		"applyChannel":"APP",
		"financingScale":"--",
		"subscribeFee":"100.00",
		"useCash":"199995246.00",
		"accountType":"CUST",
		"financingRate":"--",
		"publishId":"202610728",
		"channelType":"CMBIS"
	}
	# print(data)
	logging.info(f'{sessionDic["accountId"]} 新股认购')
	resp=requests.post(url,headers=head,json=data)
	logging.info(f'认购结果: {resp.text}')
	return resp.json()['result']['tradeOrderId']

def cancelOrderIPO(sessionDic,tradeOrderId,env='uat'):
	# 新股认购 取消认购
	url=f"http://trade-{env}.****.*****/gateway/ipo/cancelOrder"
	data={
		"sessionId":sessionDic['sessionId'],
		"accountId":sessionDic['accountId'],
		"accountName":sessionDic['accountName'],
		"acctType":sessionDic['acctType'],
		"aeCode":sessionDic['aeCode'],
		"marginMax":sessionDic['marginMax'],
		"token":sessionDic['token'],
		"operatorNo":sessionDic['operatorNo'],
		"tradeOrderId":tradeOrderId,
		"stockCode":"07028"
	}
	# print(data)
	logging.info(f'{sessionDic["accountId"]} 新股取消认购')
	resp=requests.post(url,headers=head,json=data)
	logging.info(f'取消认购结果: {resp.text}')

def preOrderDetail(sessionDic,env='uat'):
	# 查询通过聆讯 预约单号
	url=f'http://trade-{env}.****.*****/gateway/ipo/preOrderDetail'
	data={
		"sessionId":sessionDic['sessionId'],
		"accountId":sessionDic['accountId'],
		"accountName":sessionDic['accountName'],
		"acctType":sessionDic['acctType'],
		"aeCode":sessionDic['aeCode'],
		"marginMax":sessionDic['marginMax'],
		"token":sessionDic['token'],
		"publishId":171795284591557,
		"preTradeOrderId":""
	}
	resp=requests.post(url,headers=head,json=data)
	logging.info(f'{sessionDic["accountId"]} 通过聆讯订单查询结果: {resp.text}')
	try:
		return resp.json().get('result').get('preTradeOrderId')
	except:
		return None

def preOrderCancel(sessionDic,preTradeOrderId,env='uat'):
	# 查询通过聆讯 取消预约
	url=f'http://trade-{env}.****.*****/gateway/ipo/preOrderCancel'
	data={
		"sessionId":sessionDic['sessionId'],
		"accountId":sessionDic['accountId'],
		"accountName":sessionDic['accountName'],
		"acctType":sessionDic['acctType'],
		"aeCode":sessionDic['aeCode'],
		"marginMax":sessionDic['marginMax'],
		"token":sessionDic['token'],
		"publishId": 171795284591557,
		"preTradeOrderId": preTradeOrderId
	}
	resp=requests.post(url,headers=head,json=data)
	logging.info(f'{sessionDic["accountId"]} 通过聆讯取消预约结果: {resp.text}')


##################################################################################################################


if __name__ == '__main__':
	print(login_acc('919191','******','test',1))
