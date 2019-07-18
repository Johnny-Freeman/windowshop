'''
	General Market Class functions
		To store and access widely used datapoints
		Since python treats modules as namespaces, we can initiate these variables/classes as Globals
		Globals at the bottom
'''
import time
import datetime

# this is a shorthand to generate today's datetime (which also handles daylight savings!)
_now = datetime.datetime.now()
CONFIG_MARKETHOURS = {
	# Market hours dictate data gathering times
	"PreMarketOpen"	: _now.replace(hour=8, minute=30, second=0, microsecond=0),
	"MarketOpen"	: _now.replace(hour=9, minute=30, second=0, microsecond=0),
	"MarketClose"	: _now.replace(hour=16, minute=00, second=0, microsecond=0),
	
	# Trade defines program trading time
	"TradeStart"	: _now.replace(hour=9, minute=32, second=0, microsecond=0),
	"TradeEnd"		: _now.replace(hour=15, minute=57, second=0, microsecond=0),
}

def waitTime(checktime):
	# Wait if market not open
	while(datetime.datetime.now()<checktime):
		time.sleep(.2)
	return True
	
def checkTime(checktime):
	# Wait if market not open
	if datetime.datetime.now()>checktime:
		return True
	else:
		return False

def ddtime_ratioMarketTime(ratio):
	'''
		Returns timedelta object equal to ratio of market's open hours
	'''
	dt_marketDay = CONFIG_MARKETHOURS['MarketClose'] - CONFIG_MARKETHOURS['MarketOpen']
	sec_ratio = dt_marketDay.seconds * ratio
	return datetime.timedelta(seconds = sec_ratio)

class ddtime(object):
	oneday = datetime.timedelta(days=1)
	oneweek = datetime.timedelta(days=7)
	oneyear = datetime.timedelta(days=365)
	
class MarketDate(object):
	def __init__(self):
		self.ThisFriday, self.NextFriday = self.calc_ThisNextFriday()
		self.dmy_ThisFriday = self.convert2dmy(self.ThisFriday)
		self.dmy_NextFriday = self.convert2dmy(self.NextFriday)
	
	def calc_ThisNextFriday(self):
		firstfri = datetime.date.today()

		# increment until a Friday is reached, friday is denoted by #4
		while not firstfri.weekday() == 4:
			firstfri += ddtime.oneday
		
		secfri = firstfri + ddtime.oneweek
		return firstfri, secfri
		
	def convert2dmy(self, dateobj):
		# convert to DMY list for fast indexing in program
		dmy = []
		dmy.append(dateobj.day)
		dmy.append(dateobj.month)
		dmy.append(dateobj.year)
		return dmy
		
	def dmy_nextNFridays(self,N):
		# returns dmy_list of fridays starting with this friday [dmy_thisfriday, ....., dmy_Nth friday]
		if N ==0:
			return [[]]
		
		friday = self.ThisFriday
		fri_list = [self.dmy_ThisFriday]
		
		for i in range(N-1):
			friday += ddtime.oneweek
			fri_list.append(self.convert2dmy(friday))
		
		return fri_list
		
	def dmy_prevDay(self, dmy_Object):
		'''
			dmy_Object = [day,month,year]
			Need to return the previous Day as dmy_Object format
		'''
		obj_date = datetime.datetime(year=dmy_Object[2], month=dmy_Object[1], day=dmy_Object[0])
		obj_prevDate = obj_date - ddtime.oneday
		return [obj_prevDate.day, obj_prevDate.month, obj_prevDate.year]

class MarketTime(object):
	# Market hours dictate data gathering times
	PreMarketOpen	= CONFIG_MARKETHOURS['PreMarketOpen']
	MarketOpen		= CONFIG_MARKETHOURS['MarketOpen']
	MarketClose		= CONFIG_MARKETHOURS['MarketClose']
	
	# Trade defines program trading time
	TradeStart		= CONFIG_MARKETHOURS['TradeStart']
	TradeEnd		= CONFIG_MARKETHOURS['TradeEnd']

	def marketMinute(self):
		# Return minutes since market has been open
		now = datetime.datetime.now()
		now -= self.MarketOpen
		return now.seconds //60
	
	def marketMinuteSecond(self):
		# Return minutes since market has been open
		now = datetime.datetime.now()
		now -= self.MarketOpen
		return now.seconds //60, now.seconds %60

class _MarketDateTime(MarketDate, MarketTime):
	def __init__(self):
		MarketDate.__init__(self)

# *** Globals INIT(includes classes)*******************
marketdatetime = _MarketDateTime()	# holds market relevent dates and times, returns date, time, datetime objects

# *** END Globals *********************************