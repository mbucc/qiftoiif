g_accts = None

class account:
	name = ""
	type = None
	def __str__(self):
		return self.name

def stoaccts(s):
	'''Given a string, return all accounts that match.'''
	
	global g_accts
	if g_accts is None:
		fp = open('coa.iif', 'r')
		g_accts = fptoaccts(fp)
		fp.close()

	rval = []
	for a in g_accts:
		if a.name.lower().find(s.lower()) != -1:
			rval.append(a)
	return rval

def iif_stoacct(s):
	'''Given a string from an Quickbooks IIF account list eport, return 
	an account object.

	Here's a sample line from the IIF export I just made:

		>>> s='ACCNT	Checking	52	0	BANK	"1,000.00"			0	'
		>>> a = iif_stoacct(s)
		>>> a.type
		'BANK'
		>>> a.name
		'Checking'
	'''

	flds = s.split('\t')
	a = account()
	a.name = flds[1]
	a.type = flds[4]
	return a

def fptoaccts(fp):
	accounts = []

	while 1:

		l = fp.readline()
		if not l:
			break

		#
		# Skip header lines and other non-account lines.
		#

		if l[:5] != 'ACCNT':
			continue

		accounts.append(iif_stoacct(l))

	return accounts
