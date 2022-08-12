import HTMLReport,time,os,logging,argparse,traceback,threading
from uuid import uuid4
from testSuite.suite import *
from business.login_boss import login_boss
from common.apiCenter import login_acc,cardOperate,signAgreement,openMarket
from common.tools import getWebDriver,sendMail,moveFiles
from testData.data import accountPool
try:
	from config import host
except:
	host=''
from config import bossAcc

# LuckyFrame
def getParser():
	parser=argparse.ArgumentParser(description='Web端UI自动测试',formatter_class=argparse.RawTextHelpFormatter)
	parser.add_argument('-a',dest='account',help="指定测试账户号",required=False,default='917668')
	parser.add_argument('-e',dest='env',help="指定运行环境(默认 UAT)：\n\tUAT\tUAT环境\n\tTEST\tTEST环境",required=False,default='uat')
	parser.add_argument('-s',dest='suite',help="指定需要执行的用例集(默认 all):\n\tall\t\t所有用例集\n\tlogin\t\t登录用例集\n\ttrade\t\t股票交易用例集\n\tstar\t\t自选用例集\n\tpfund\t\t私募基金下单\n\tbond\t\t债券下单\n\tsp\t\t结构化交易下单",required=False,default='all')
	parser.add_argument('--sendMail',help="自动发送邮件",action='store_true',required=False)
	parser.add_argument("--receiver",help=argparse.SUPPRESS,required=False)
	parser.add_argument("--fromInfo",help=argparse.SUPPRESS,required=False)
	parser.add_argument("--headless",help=argparse.SUPPRESS,action='store_true',required=False)
	args=parser.parse_args()
	return args

def main():
	try:
		sessionDic=login_acc(args.account,accountPool[args.account],env=args.env)
		threading.Thread(target=openMarket,args=(sessionDic,args.env,)).start()#开通市场
		threading.Thread(target=cardOperate,args=(sessionDic,args.env,)).start()#港股行情卡
		threading.Thread(target=signAgreement,args=(sessionDic,args.env,)).start()#美股行情卡
	except:pass
	args.timeStr=f"{time.strftime('%Y%m%d%H%M%S')}_{str(uuid4())[:6]}"
	driver=getWebDriver(setwindow=1,headless=args.headless)
	
	driver2=getWebDriver(setwindow=1,headless=1,wire=1)
	login_boss(driver2,bossAcc[args.env],args.env,tradingmo='442')
	driver2.quit()

	url=f'http://etrade-{args.env}.****.******/#/'
	# driver.get(url)
	
	suites=loadSuite(driver,args)

	reportURL=f'{host}/{args.timeStr}'
	HTMLReport.TestRunner(
		title="Web端UI自动测试",
		description=f'运行环境: <span class="info">{args.env.upper()}</span></br>地址: <span class="info">{url}</span></br>',
		output_path=f'report/{args.timeStr}',
		report_file_name='index',
		sequential_execution=True,#按照套件添加(addTests)顺序执行
		tries=2,delay=3,retry=True,
	).run(suites)
	driver.quit()

	# text=open(os.path.expanduser(os.path.join(webPath,args.timeStr,'index.html')),'r',encoding='utf-8').read()
	text=open(os.path.join('report',args.timeStr,'index.html'),'r',encoding='utf-8').read()
	try:
		moveFiles(args.timeStr,'copy')
		print('报告链接：',reportURL)
		foot=f'<p>网页版请<a href="{reportURL}">点击这里</a>查看(提示：请用 CMBI 网络访问)</p><br/>'
	except:
		# traceback.print_exc()
		foot=''
		print(f'\n报告链接: report/{args.timeStr}')
	

	if args.sendMail:
		platformName=args.env.upper()
		sendMail(f'{foot}{text}',platformName,fromInfo=args.fromInfo,cusReceiver=args.receiver)
	return reportURL,args.timeStr

if __name__=='__main__':
	args=getParser()
	args.env=args.env.lower()
	reportURL,timeStr=main()
