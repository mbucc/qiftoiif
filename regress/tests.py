import unittest
import doctest

import sys
sys.path.append('../src')

import coa
import vendors
import interpreter
import vendoraccount

suite = unittest.TestSuite()

for mod in (coa, vendors, interpreter, vendoraccount):
	suite.addTest(doctest.DocTestSuite(mod))

runner = unittest.TextTestRunner()
runner.run(suite)

