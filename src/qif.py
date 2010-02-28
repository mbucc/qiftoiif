# Classes that represent QIF data.


class list:
	type = None
	transactions = []
	def __unicode__(self):
		return "Type : %s\nTrx  : %d\n%s" % (\
		    self.type, 
		    len(self.transactions),
		    "\n".join([str(t) for t in self.transactions])
		    )
#		return "Type : %s\n%s" % (\
#		    self.type, 
#		    "\n".join([str(t) for t in self.transactions])
#		    )
	def __str__(self):
		return self.__unicode__()

class basetransaction:
	pass

class checkingtransaction(basetransaction):
	def __init__(self):
		self.clear()
	def __unicode__(self):
		return "%10s%12.2f    %s" %  ( \
		    self.date, 
		    self.amount_in_pennies/100.0,
		    self.payee
		    )
	def __str__(self):
		return self.__unicode__()
	def clear(self):
		self.amount_in_pennies = 0.0
		self.cleared_status = None
		self.date = None
		self.memo = None
		self.payee = None
		self.payee_address = None
		self.category_or_transfer = None
		self.check_number = None

class investmenttransaction(basetransaction):
	pass
	

