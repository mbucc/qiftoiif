# 
# Classes that represent QIF data.
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


class list:
	type = None
	transactions = []
	def __unicode__(self):
		return "Type : %s\nTrx  : %d\n%s" % (\
		    self.type, 
		    len(self.transactions),
		    "\n".join([str(t) for t in self.transactions])
		    )
	def __str__(self):
		return self.__unicode__()

class basetransaction:
	pass

class checkingtransaction(basetransaction):
	def __init__(self):
		self.amount_in_pennies = 0.0
		self.cleared_status = None
		self.date = None
		self.memo = None
		self.security_name = ''
		self.security_price = 0
		self.share_quantity = 0
		self.commission_cost = 0
	def __str__(self):
		return "%10s%12.2f    %s" %  ( \
		    self.date, 
		    self.amount_in_pennies/100.0,
		    self.security_name
		    )

class investmenttransaction(basetransaction):
	def __init__(self):
		self.amount_in_pennies = 0.0
		self.cleared_status = None
		self.date = None
		self.memo = None
		self.payee = None
		self.payee_address = None
		self.category_or_transfer = None
		self.check_number = None
	def __str__(self):
		return "%10s%12.2f    %s" %  ( \
		    self.date, 
		    self.amount_in_pennies/100.0,
		    self.payee
		    )
