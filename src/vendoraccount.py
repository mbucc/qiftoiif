# Store last account assigned to vendor, as well as vendors not in iif.
# Persist this data to disk.

import csv
import errno
import sys

DIALECT_NAME = 'va_name'
DEFAULT_DATA_FILENAME = 'vendoraccount.csv'
V_COLNAME = 'vendor'
A_COLNAME = 'account'

class VendorAccount:
	'''Wrap up a tab-delimted file that stores vendor name and account.'''
	def __init__(self, fn = DEFAULT_DATA_FILENAME):
		'''
		Should handle case where no persisted data yet.

			>>> va = VendorAccount('/tmp/asdflkjasdflkjasd')
			>>> va.vendortoaccount
			{}
		'''
		csv.register_dialect(
		    DIALECT_NAME, 
		    delimiter = '\t',
		    quoting = csv.QUOTE_NONE,
		    lineterminator = '\n',
		    )
		self.fn = fn
		self.vendortoaccount = {}
		self.fieldnameorder = (V_COLNAME, A_COLNAME)
		try:
			print >> sys.stderr, \
			    "\nVendorAccount: loading '%s' ..." % (self.fn, )
			reader = csv.DictReader(
			    open(self.fn, 'rb'), 
			    dialect = DIALECT_NAME
			    )
			for row in reader:
				v = row[V_COLNAME]
				a = row[A_COLNAME]
				self.vendortoaccount[v] = a
			print >> sys.stderr, " done\n"
			# XXX: validate accounts against coa.iif
		except IOError, e:
			if e.errno != errno.ENOENT:
				raise
	def __len__(self):
		return len(self.vendortoaccount)
	def __str__(self):
		return "VendorAccounts from '%s'" % (self.fn,)
	def save(self):
		'''Persist to disk.

			>>> fn = './testva.csv'
			>>> import os, errno
			>>> try:
			...     os.remove(fn)
			... except OSError, ose:
			...     if ose.errno != errno.ENOENT:
			...         raise
			... except IOError, ioe:
			...     if ioe.errno != errno.ENOENT:
			...         raise
			>>> va = VendorAccount(fn)
			>>> va.set('my vendor', 'my account')
			>>> va.save()
			>>> fp = open(fn, 'r')
			>>> l = fp.readline()
			>>> v,a = l.split('\\t')
			>>> v
			'vendor'
			>>> a
			'account\\n'
			>>> l = fp.readline()
			>>> v,a = l.split('\\t')
			>>> v
			'my vendor'
			>>> a
			'my account\\n'
		'''

		rows = [ {V_COLNAME:x, A_COLNAME:y} \
		    for x,y in self.vendortoaccount.items() ]
		fp = open(self.fn, 'wb')
		writer = csv.DictWriter(fp, self.fieldnameorder, 
		    dialect = DIALECT_NAME)
		writer.writerow(dict((cn,cn) for cn in self.fieldnameorder))
		writer.writerows(rows)
		fp.close()

	def set(self, vendor, account):
		if not vendor:
			raise ValueError("VendorAccount.set(): empty vendor")
		if not account:
			raise ValueError("VendorAccount.set(): empty account")
		self.vendortoaccount[vendor] = account

	def get(self, vendor):
		'''Return default account on file for vendor, empty string
		if none.
		'''
		if not vendor:
			raise ValueError("VendorAccount.get(): empty vendor")
		if not self.vendortoaccount.has_key(vendor):
			return ''
		return self.vendortoaccount[vendor]
	