g_vendors = None

class Vendor:
	name = ""
	default_account = None
	def __str__(self):
		return self.name

def iif_stovendor(s):
	'''Given a string from an Quickbooks IIF vendor list eport, return 
	an vendor object.

	Here's a sample line from the IIF export I just made:

		>>> s = 'VEND\\t145 University Dr\\t567\\t0\\t\\t145 University Dr\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\t\\tN'
		>>> v = iif_stovendor(s)
		>>> v.name
		'145 University Dr'
	'''

	if s[-1] == '\n':
		s = s[:-1]
	flds = s.split('\t')
	if len(flds) < 2:
		if len(flds) == 1:
			emsg = "only 1 field in '%s'" % (s,)
		else:
			emsg = "only %d fields in '%s'" % (len(flds), s)
		raise ValueError(emsg)
	a = Vendor()
	a.name = flds[1]
	return a

def fptovendors(fp):
	vendors = []

	while 1:

		l = fp.readline()
		if not l:
			break

		#
		# Skip header lines and other non-vendor lines.
		#

		if l[:4] != 'VEND':
			continue

		vendors.append(iif_stovendor(l))
	return vendors

def stovendors(s, fn = 'vendors.iif'):
	'''Given a string, return all vendors that match.'''
	
	global g_vendors
	if g_vendors is None:
		fp = open(fn,  'r')
		g_vendors = fptovendors(fp)
		if len(g_vendors) == 1:
			print "Loaded 1 vendor from %s." % (fn,)
		else:
			print "Loaded %d vendors from %s" % (len(g_vendors),fn)
		fp.close()

	rval = []
	for a in g_vendors:
		if a.name.lower().find(s.lower()) != -1:
			rval.append(a)
	return rval

