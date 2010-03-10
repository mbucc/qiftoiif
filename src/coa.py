# 
# Copyright (c) 2010 Mark Bucciarelli <mkbucc@gmail.com>
# 
# Permission to use, copy, modify, and distribute this software
# for any purpose with or without fee is hereby granted, provided
# that the above copyright notice and this permission notice
# appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING
# FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
# CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

g_accts = None

class Account:
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

		>>> s='ACCNT\\tChecking\\t52\\t0\\tBANK\\t"1,000.00"\\t\\t\\t0\\t'
		>>> a = iif_stoacct(s)
		>>> a.type
		'BANK'
		>>> a.name
		'Checking'

	'''

	flds = s.split('\t')
	if len(flds) < 5:
		if len(flds) == 1:
			emsg = "only 1 field in '%s'" % (s,)
		else:
			emsg = "only %d fields in '%s'" % (len(flds), s)
		raise ValueError(emsg)
	a = Account()
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
