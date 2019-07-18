'''
	Classes to hold information regarding the expiration dates of Options
'''

import datetime

class StrikePriceChart(object):
	'''
		To hold lists of strike prices for ONE symbol so no need to fetch using more requests
	'''
	def __init__(self, tick):
		# 0 = current week, 1 = next week, [[list],[],[]] format[week#][strikelist]
		'''
			[
				<week1> [strike list, 10, 20, 30, ..],
				<week2> [strike list, 10, 20, 30, ..],
				<week3> [...],
				...
			]
		'''
		self.strikechart = []
		
		self.symbol = tick
	
	def existWeeklyList(self, N):
		#checks if consecutive strike list already exists
		if len(strikechart) >= (N-1):
			return True
		else:
			return False

class StrikePriceStoreManager(object):
	'''
		Wrapper to hold and manage dict for StrikePriceChart
		https://stackoverflow.com/questions/4014621/a-python-class-that-acts-like-dict#23976949
		
		list_NWeeks = [to be populated with [day,month,year], [dmy_fridays], [expiration dates<week3>], [<week4>], [...]]
		* should create function which fills this list AND checks the list for irregular dates(eg. Thursday)
	'''
	def __init__(self):
		self._dict_symbol_strikecharts = {}
		self.list_NWeeks = []
		
		self.lastupdated = datetime.date.today()
		
	def __setitem__(self, key, item):
		self._dict_symbol_strikecharts[key] = item

	def __getitem__(self, key):
		return self._dict_symbol_strikecharts[key]

	def __repr__(self):
		return repr(self._dict_symbol_strikecharts)

	def __len__(self):
		return len(self._dict_symbol_strikecharts)
	
	def symbolstored(self, symbol):
		self.checksameday()

		# Does symbol exist in dict?
		try:
			y = self._dict_symbol_strikecharts[symbol]
			return True
		except:
			return False
	
	def checksameday(self):
		# Function useful if program has been continuous
		if self.lastupdated == datetime.date.today():
			return True
		else:
			#reinit
			self.__init__()
			return False
			
	def NEW_StrikePriceChart(self, symbol):
		if not type(symbol)==type('str'):
			raise ValueError('Symbols must be string format')
		
		self._dict_symbol_strikecharts[symbol] = StrikePriceChart(symbol)
			
	def SET_nextNExpirations(self, a_list):
		if not type(a_list)== type([]):
			raise ValueError('List of Expiration Dates must be in a list')
		elif len(a_list)==0:
			raise ValueError('List of Expiration Dates cannot be empty')
		elif not type(a_list[0])== type([]):
			raise ValueError('List of Expiration Dates must be of form [  [day,month,year] , [d,m,y] , [d,m,y] ,...  ]')
		elif ( not len(a_list[0])==3 ) and (not type(a_list[0][0]) == type[1]) :
			raise ValueError('List of Expiration Dates must be of form [  [day,month,year] , [d,m,y] , [d,m,y] ,...  ]')
		
		self.list_NWeeks = a_list
	
	def GRAB_dmy_nextNExpirations(self, N):
		'''
			Returns first N <dmy_Fridays> [day,month,year] from self.list_NWeeks as list
		'''
		if len(self.list_NWeeks) ==0:
			raise ValueError('obj.list_NWeeks must be manually declared first, likely in init() or main()')
		elif N > len(self.list_NWeeks):
			raise ValueError('N number of weekly Expirations must be less-than-equal to length(obj.list_NWeeks)')
		
		return self.list_NWeeks[:N]
	
# StrikePriceStore = StrikePriceStoreManager()	# Initiate Store