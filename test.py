import sys,os,HTMLReport,traceback
# from common.system_boss import *
from common.system_pmo import *
from common.tools import save_to_excel
# login_boss_api('uat')
# fundNameList=[]
# for curr in ['HKD','USD','CNY']:
# 	for i in range(1):
# 		fundNameList.append(addPfund(curr,'uat'))
# print(fundNameList)

# print(addPfund('USD','uat'))
# print(add_structure('HKD','uat'))

# for pfundName in ['基金名称05-25 09-47-01','基金名称05-25 09-47-03']:
# productCode=queryPfundCode('基金名称07-28 15-09-34','uat')
# print(productCode)


# print(getPower('M803901','P20220726P064USD','pFundOrder','uat'))


'''
# 私募基金
# prdCode='S20220803S117USD'
env='uat'
side='SELL'
# side='BUY'
prdCodeList=[
"P20220728P103USD"
]
for prdCode in prdCodeList:
	# mergerOrder(queryOrders(prdCode,side))
	orderInfo=get_groupId(prdCode,env,1)

	complete(orderInfo['groupId'],env)
	save_to_excel(orderInfo['groupId'],prdCode,orderInfo['productNameCn'],orderInfo['totalAmount'],side=side,status='Success')
	pFund_upload()
	complete_confirm(orderInfo['groupId'],env)

# print(queryOrders_bond(prdCode,side))
'''

# 结构化
env='uat'
side='SELL'
# side='BUY'
prdCodeList=[

]
for prdCode in prdCodeList:
	try:
		mergerOrder_struct(queryOrders_struct(prdCode,side))
		groupId=get_groupId_struct(prdCode,env)
		edit_struct(groupId,env,side)
		complete_struct(groupId,env)
	except:
		traceback.print_exc()

# queryOrders_struct('','SELL')