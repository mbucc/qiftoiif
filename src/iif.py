#
# Convert transaction to IIF.  Rudimentary, not sure it's right; for
# example, what't the IIF for an ACH transfer?  But it works and I
# need to get taxes done.
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


def header():
	a = []
	a.append("!TRNS\tTRNSTYPE\tDATE\tACCNT\tAMOUNT\tNAME\tDOCNUM")
	a.append("!SPL\tACCNT\tAMOUNT")
	a.append("!ENDTRNS")
	return '\n'.join(a)

def qiftrxtoiif(qiftrx, account):
	q = qiftrx.qifdata
	if not q:
		raise ValueError('qiftrx has no QIF data')
	if not qiftrx.account:
		raise ValueError('qiftrx has no account')

	#
	# Different IIF format for checks and transfers.
	#
	#        1: Date
	#        2: Check Number
	#        3: Description (usually vendor)
	#        4: Type (e.g., DEBIT CARD PURCHSE)
	#        5: Amount
	#
	# print "TRNS\tCHECK\t" $1 "\t" account "\t" $5 "\t" $3 "\t" $2
	#

	amt = q.amount_in_pennies / float(100)
	a = []
	if q.check_number is not None:
		b = [
		    'TRNS',
		    'CHECK',
		    q.date,
		    account,
		    '%.2f' % (amt,),
		    q.payee,
		    '%d' % (q.check_number,),
		    ]
		a.append('\t'.join(b))
	else:
		b = [
		    'TRNS',
		    'GENERAL JOURNAL',
		    q.date,
		    account,
		    '%.2f' % (amt,),
		    q.payee,
		    '%d' % (q.check_number,),
		    ]
		a.append('\t'.join(b))
	b = [
	   'SPL',
	   qiftrx.account.name,
	   '%d' % (-1 * amt,),
	   ]
	a.append('\t'.join(b))
	a.append("ENDTRNS")
	return '\n'.join(a)
