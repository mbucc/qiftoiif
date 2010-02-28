import unittest
import doctest

import sys
sys.path.append('../src')

import coa


suite = unittest.TestSuite()

for mod in (coa, ):
	suite.addTest(doctest.DocTestSuite(mod))
	runner = unittest.TextTestRunner()
	runner.run(suite)

