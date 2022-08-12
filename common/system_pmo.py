import requests,time,logging,jsonpath
from .tools import readCookie

def requests_pmo(methmod,path,env='uat',upload=None,**kwargs):
	head={
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36 Edg/103.0.1264.71',
		'Content-Type':'application/json; charset=UTF-8',
		'Authorization':readCookie(f'pmo_{env}'),
		'Connection':'close',
	}
	if upload:head['Content-Type']=kwargs['data'].content_type
	url=f'http://tradingmo-{env}.****.******{path}'
	logging.info(f'{methmod} 请求: {url}')
	resp=requests.request(methmod,url,headers=head,**kwargs)
	try:
		result=resp.json()
	except:
		result=resp.text
	return result

######################################## 私募基金 ##################################################################
def queryOrders(prdCode,side='BUY',env='uat'):
	# 查询私募基金订单id
	path=f'/tmo-portal/gateway/tmo-portal//tmo-pbot-private-fund/rest/1.0/private-fund/orders?productCode={prdCode}&tradeType={side}'
	respJson=requests_pmo('GET',path,env)
	logging.info(f'{env} 查询私募基金订单 {prdCode} 结果: {respJson}')
	return jsonpath.jsonpath(respJson,'$..dataList[?(@.orderReqNoList!=None)]')[0]['orderReqNoList']

def mergerOrder(orderReqNoList,env='uat'):
	# 生成合单
	path='/tmo-portal/gateway/tmo-portal//tmo-pbot-private-fund/rest/1.0/private-fund/orders/action/mergerOrder'
	data={"orderReqNoList":orderReqNoList}
	respJson=requests_pmo('POST',path,env,json=data)
	logging.info(f'{env} 合并私募订单 {orderReqNoList} 结果: {respJson}')
	# {"status":{"code":"0","message":""},"data":""}

def get_groupId(prdCode,env='uat',moreInfo=0):
	#查询合单ID
	path=f'/tmo-portal/gateway/tmo-portal//tmo-pbot-private-fund/rest/1.0/private-equity/placeOrder/pageList?pageSize=10&pageNum=1&orderStatus=Waiting&productName=&tradeStartDate=&tradeEndDate=&orderChannel=&productCode={prdCode}'
	respJson=requests_pmo('GET',path,env)
	logging.info(f'{env} 查询私募基金订单 {prdCode} 合单ID 结果: {respJson}')
	if moreInfo:
		return {
			'groupId':jsonpath.jsonpath(respJson,'$..groupId')[0],
			'productNameCn':jsonpath.jsonpath(respJson,'$..productNameCn')[0],
			'productNameEn':jsonpath.jsonpath(respJson,'$..productNameEn')[0],
			'totalAmount':jsonpath.jsonpath(respJson,'$..totalAmount')[0] or jsonpath.jsonpath(respJson,'$..totalShares')[0],
		}
	else:
		return jsonpath.jsonpath(respJson,'$..groupId')[0]

def complete(groupId,env='uat'):
	# 完成下单
	path='/tmo-portal/gateway/tmo-portal//tmo-pbot-private-fund/rest/1.0/private-equity/placeOrder/complete'
	data={
		"groupId":groupId,
		"navDate":None,
		"nav":None,
		"settledDate":time.strftime("%Y-%m-%d"),
		"tradeDate":time.strftime("%Y-%m-%d"),
		"seriesNo":time.strftime("%Y%m%d")
	}
	respJson=requests_pmo('POST',path,env,json=data)
	logging.info(f'{env} 完成私募订单 {groupId} 结果: {respJson}')
	# {"status":{"code":"0","message":""},"data":""}

def pFund_upload(env='uat'):
	# 上传Excel
	from requests_toolbelt import MultipartEncoder
	path='/tmo-portal/gateway/tmo-portal//tmo-pbot-private-fund/rest/1.0/privateFund/confirmation/import'
	bin_data=MultipartEncoder(
		fields={
			'file': ('tmp.xlsx', open('testData/tmp.xlsx', 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')#第三个参数是文件
		}
	)
	respJson=requests_pmo('POST',path,env,upload=1,data=bin_data)
	logging.info(f'{env} 上传Excel 结果: {respJson}')

def importDetail(groupId,env='uat'):
	# 查询订单号
	path=f'/tmo-portal/gateway/tmo-portal//tmo-pbot-private-fund/rest/1.0/privateFund/confirmation/importDetail?groupId={groupId}'
	respJson=requests_pmo('GET',path,env)
	logging.info(f'{env} 查询私募基金合单{groupId}的订单号 结果: {respJson}')
	return jsonpath.jsonpath(respJson,'$..reqNo')[0]

def complete_confirm(groupId,env='uat'):
	# 确认完成订单
	reqNo=importDetail(groupId,env)
	path='/tmo-portal/gateway/tmo-portal//tmo-pbot-private-fund/rest/1.0/privateFund/confirmation/complete'
	data=[{"groupId":groupId,"reqNo":reqNo,"modifyAmt":"500000","modifyVol":"500000"}]
	respJson=requests_pmo('POST',path,env,json=data)
	logging.info(f'{env} 确认完成私募订单 {groupId} 结果: {respJson}')

######################################## 结构化 ##################################################################
def queryOrders_struct(prdCode,side='BUY',env='uat'):
	# 查询结构化订单id
	path=f'/tmo-portal/gateway/tmo-portal//tmo-pbot-structure/rest/1.0/orders?productCodeOrIsin={prdCode}&tradeType={side}&pageSize=10000&pageNum=1&orderStatus=Waiting'
	respJson=requests_pmo('GET',path,env)
	logging.info(f'{env} 查询结构化订单 {prdCode} 结果: {respJson}')
	return jsonpath.jsonpath(respJson,'$..reqNoChannel')

def mergerOrder_struct(orderReqNoList,env='uat'):
	# 生成合单
	path='/tmo-portal/gateway/tmo-portal//tmo-pbot-structure/rest/1.0/orders/action/mergerOrder'
	data={"reqNoChannelList":orderReqNoList}
	respJson=requests_pmo('POST',path,env,json=data)
	logging.info(f'{env} 合并结构化订单 {orderReqNoList} 结果: {respJson}')

def get_groupId_struct(prdCode,env='uat'):
	#查询合单ID
	path=f'/tmo-portal/gateway/tmo-portal//tmo-pbot-structure/rest/1.0/structure/placeOrder/pageList?productCode={prdCode}&status=Waiting&pageSize=10&pageNum=1'
	respJson=requests_pmo('GET',path,env)
	logging.info(f'{env} 查询结构化订单 {prdCode} 合单ID 结果: {respJson}')
	return jsonpath.jsonpath(respJson,'$..groupId')[0]	

def get_orderDetail_struct(groupId,env='uat'):
	path=f'/tmo-portal/gateway/tmo-portal//tmo-pbot-structure/rest/1.0/structure/placeOrder/detail?groupId={groupId}'
	respJson=requests_pmo('GET',path,env)
	logging.info(f'{env} 查询结构化订单 {groupId} 订单详情 结果: {respJson}')
	return respJson

def edit_struct(groupId,env='uat',side='BUY'):
	path='/tmo-portal/gateway/tmo-portal//tmo-pbot-structure/rest/1.0/structure/placeOrder/edit'
	detail=get_orderDetail_struct(groupId,env)['data']
	data={
		"knockDownPrice": "5",
		"tradeDate": time.strftime("%Y-%m-%d"),
		"settlementDate": jsonpath.jsonpath(detail,'$..orderTime')[0],
		"counterparty": "SCBHK",
		"orderList": jsonpath.jsonpath(detail,'$..orderList')[0],
		"createTime": jsonpath.jsonpath(detail,'$..createTime')[0],
		"groupId": groupId,
		"id": jsonpath.jsonpath(detail,'$..id')[0],
		"investmentCurrency": jsonpath.jsonpath(detail,'$..investmentCurrency')[0],
		"paperPrice": jsonpath.jsonpath(detail,'$..paperPrice')[0],
		"productCode": jsonpath.jsonpath(detail,'$..productCode')[0],
		"productName": jsonpath.jsonpath(detail,'$..productName')[0],
		"productType": jsonpath.jsonpath(detail,'$..productType')[0],
		"status": jsonpath.jsonpath(detail,'$..status')[0],
		"tradeType": jsonpath.jsonpath(detail,'$..tradeType')[0],
	}
	if side=='BUY':
		data["amount"]=jsonpath.jsonpath(detail,'$..amount')[0]
	else:
		data["shares"]=jsonpath.jsonpath(detail,'$..shares')[0]
	respJson=requests_pmo('POST',path,env,json=data)
	logging.info(f'{env} 修改结构化订单 {groupId} 结果: {respJson}')

def complete_struct(groupId,env='uat'):
	# 结构化完成下单
	path='/tmo-portal/gateway/tmo-portal//tmo-pbot-structure/rest/1.0/structure/placeOrder/complete'
	data={"groupId":groupId}
	respJson=requests_pmo('POST',path,env,json=data)
	logging.info(f'{env} 完成结构化订单 {groupId} 结果: {respJson}')
