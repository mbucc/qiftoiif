import unittest
import doctest

import sys
sys.path.append('../src')

import coa
import vendors
import interpreter

suite = unittest.TestSuite()

for mod in (coa, vendors, interpreter):
	suite.addTest(doctest.DocTestSuite(mod))

runner = unittest.TextTestRunner()
runner.run(suite)

