# Store last account assigned to vendor, as well as vendors not in iif.
# Persist this data to disk.

import csv
import errno
import sys

DIALECT_NAME = 'va_name'
DEFAULT_DATA_FILENAME = 'vendoraccount.csv'
V_COLNAME = 'vendor'
A_COLNAME = 'account'

g_vendoraccount = None

class VendorAccount:
	'''Wrap up a tab-delimted file that stores vendor name and account.'''
	def __init__(self, fn = DEFAULT_DATA_FILENAME):
		'''
		Should handle case where no persisted data yet.

			>>> va = VendorAccount('/tmp/asdflkjasdflkjasd')
			>>> va.d
			{}
		'''
		csv.register_dialect(
		    DIALECT_NAME, 
		    delimiter = '\t',
		    quoting = csv.QUOTE_NONE,
		    lineterminator = '\n',
		    )
		self.fn = fn
		self.d = {}
		self.fieldnameorder = (V_COLNAME, A_COLNAME)
		try:
			reader = csv.DictReader(
			    open(self.fn, 'rb'), 
			    dialect = DIALECT_NAME
			    )
			for row in reader:
				v = row[V_COLNAME]
				a = row[A_COLNAME]
				self.d[v] = a
			print >> sys.stderr, \
			    "loaded %d entries from '%s'." % \
			    (len(self.d), self.fn)
			# XXX: validate accounts against coa.iif
		except IOError, e:
			if e.errno != errno.ENOENT:
				raise
			print >> sys.stderr, \
			    "loaded 0 entries from '%s', none saved  yet." % \
			    (self.fn,)
	def __len__(self):
		return len(self.d)
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
		    for x,y in self.d.items() ]
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
		self.d[vendor] = account

	def get(self, vendor):
		'''Return default account on file for vendor, empty string
		if none.
		'''
		f = 'VendorAccount.get()'
		if not vendor:
			raise ValueError("%s: empty vendor" % (f,))
		t = type(vendor)
		if t != type('s') and t != type(u's'):
			raise ValueError("%s: vendor is not a string" % (f,))
		if self.d.has_key(vendor):
			return self.d[vendor]
		else:
			return ''
	
def vendornametoaccount(vendor, fn = DEFAULT_DATA_FILENAME):
	global g_vendoraccount
	if not g_vendoraccount:
		g_vendoraccount = VendorAccount(fn)
	return g_vendoraccount.get(vendor)

def vendoraccount():
	return g_vendoraccount
