import unittest
from common.parameter import ParameTestCase

from testCase.testLogin import TestLogin
from testCase.testTrade import TestTrade
from testCase.testSelfselected import TestSelfselected

from testCase.testPfund import TestPfund
from testCase.testPfund_uat import TestPfund_uat

from testCase.testBond import TestBond
from testCase.testBond_test import TestBond_test
from testCase.testBond_data import TestBond_data
from testCase.testBond_uat import TestBond_uat

from testCase.testStructured import TestStructured
from testCase.testStructured_test import TestStructured_test
from testCase.testStructured_uat import TestStructured_uat

def loadSuite(driver,args):
	testCasesDic={
		'login':TestLogin,
		'trade':TestTrade,
		'star':TestSelfselected,
		
		'pfund':TestPfund,
		'pfund_uat':TestPfund_uat,

		'bond':TestBond,
		'bond_test':TestBond_test,
		'bond_data':TestBond_data,
		'bond_uat':TestBond_uat,

		'sp':TestStructured,
		'sp_test':TestStructured_test,
		'sp_uat':TestStructured_uat,
	}
	testSuite=unittest.TestSuite()
	for sName in args.suite.split():
		if sName=='all':
			for suiteName,testClass in testCasesDic.items():
				__testClass=testCasesDic[suiteName]
				__testClass.args=args
				__testClass.driver=driver
				testSuite.addTest(ParameTestCase.paramed(__testClass,driver=driver,args=args))
		else:
			try:
				__testClass=testCasesDic[sName]
				__testClass.args=args
				__testClass.driver=driver
				testSuite.addTest(ParameTestCase.paramed(__testClass,driver=driver,args=args))
			except KeyError:
				raise Exception(f'未知的测试用例集: {sName}')
	return testSuite

if __name__=='__main__':
	pass