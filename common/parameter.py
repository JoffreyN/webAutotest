import unittest
 
class ParameTestCase(unittest.TestCase):
	def __init__(self, methodName='runTest', **kwords):
		super(ParameTestCase, self).__init__(methodName)
		for k,v in kwords.items():
			if type(v)==str:
				exec(f'self.{k}="{v}"')
			else:
				exec(f'self.{k}=v')
 
	@staticmethod
	def paramed(testcase_klass, **kwords):
		testloader=unittest.TestLoader()
		testnames=testloader.getTestCaseNames(testcase_klass)
		suite=unittest.TestSuite()
		for name in testnames:
			suite.addTest(testcase_klass(name,**kwords))
		return suite