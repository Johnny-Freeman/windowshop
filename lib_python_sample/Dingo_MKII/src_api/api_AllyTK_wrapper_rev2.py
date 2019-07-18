'''
	Wrapper to manage the AllyTK api
	
	Ideal use of this api is centered on running in one process and generating threads to grab string data
	
'''
from datetime import datetime
import re, time

from utils import marketTime as MarketTimeManager
from classes import API_Thresholds

import api_AllyTK_rev2 as AllyTK

# ******START AllyTK Settings*************
from config import AllyTK__SETTINGS
ratelimits = API_Thresholds.RateLimits('ALLYTK', AllyTK__SETTINGS.CONFIG_API)

Debug = False
if Debug:
	from toolkit import speedtest

# *******END AllyTK Settings********************
def init():
	AllyTK.login()

def PRECHECK_StocksList(list_symbols):
	'''
		Checking only the options list
	'''
	# Wait time between requests
	wait_time = ratelimits.heartbeat / ratelimits.allowance_Public
	
	list_good_stocks = []
	list_bad_stocks = []
	
	for symbol in list_symbols:
		if not VET_ERROR_AllyTK_respString(	GET_1minCandle(symbol)):
			list_good_stocks.append(symbol)
		else:
			list_bad_stocks.append(symbol)
			
		time.sleep(wait_time)

	return list_good_stocks,list_bad_stocks

def PRECHECK_OptionsList(list_symbols, N=1):
	'''
		Checking only the options list
	'''
	# Wait time between requests
	wait_time = ratelimits.heartbeat / ratelimits.allowance_Public
	
	list_good_options = []
	list_bad_options = []
	
	for symbol in list_symbols:
		if not VET_ERROR_AllyTK_respString(	GET_OptionNweekData(symbol,N)):
			list_good_options.append(symbol)
		else:
			list_bad_options.append(symbol)
			
		time.sleep(wait_time)
	
	return list_good_options,list_bad_options
	
def PRECHECK_SymbolsList(list_symbols, N=1):
	'''
		Keep in mind should be ran at least approximately 2 second per symbol prior for = value of heartbeat / Public_Ratelimit in seconds
		Will auto fail any if it doesn't pass either one
	'''
	list_good_round1_stock = []
	list_good_round2_options = []
	list_bad_stock = []
	list_bad_options = []
	
	# Wait time between requests
	wait_time = ratelimits.heartbeat / ratelimits.allowance_Public
	
	for symbol in list_symbols:
		if not VET_ERROR_AllyTK_respString(	GET_1minCandle(symbol)):
			list_good_round1_stock.append(symbol)
		else:
			list_bad_stock.append(symbol)
			
		time.sleep(wait_time)
		
	for symbol in list_good_round1_stock:
		if not VET_ERROR_AllyTK_respString(	GET_OptionNweekData(symbol,N)):
			list_good_round2_options.append(symbol)
		else:
			list_bad_options.append(symbol)
			
		time.sleep(wait_time)
		
	return list_good_round1_stock, list_good_round2_options, list_bad_stock, list_bad_options
	
def VET_ERROR_AllyTK_respString(respString):
	'''
		Verifies data meets ALLYTK integrity, Returns False by convention of Error
			- Should be ran in init function to check if a list of symbols from this source is reliable
		
		space = \s*
		front_block	= '{ "response":{'				14 characters at beginning,	re_pattern = '\{\s*"[rR]esponse"\s*:\s*\{'
		rear_block	= ', "error": "Success" } }'	24 characters at the end,	re_pattern = '\s*"[eE]rror"\s*:\s*"[Ss]uccess"\s*\}\s*\}'
		
		Using regular expressions since I'm worried about variable spaces, and capital letters, AllyTK isn't always trustworthy
		https://docs.python.org/2/library/re.html
	'''
	if not type(respString) == type('str'):
		print'Warning45: possible timeout by AllyTK'
		# Error found = True
		return True
	
	# buffer zone to search for key, about 50% more
	# Intra-Bracket locations [1,2,3 ,..... ,-3,-2,-1]
	loc_front = 21
	loc_rear = -36
	
	# Rare for these to change, unless AllyTK updates their API
	# Strings to test data quality, reject string if fails
	test_frontpattern = re.compile('\{\s*"[rR]esponse"\s*:\s*\{')
	test_rearpattern = re.compile('\s*"[eE]rror"\s*:\s*"[Ss]uccess"\s*\}\s*\}')
	
	data_front = respString[:loc_front]
	data_rear = respString[loc_rear:]
	
	check_front = re.search(test_frontpattern, data_front)
	check_rear = re.search(test_rearpattern, data_rear)
	
	if (check_front==None) or (check_rear==None):
		# Error found = True
		return True
	else:
		# no Error
		return False
		
def VET_ERROR_multi_respStrings(list_respStrings):
	'''
		Returns a list of ERROR_found True/False per String
	'''
	list_error_found = []
	for _s in list_respStrings:
		list_error_found.append(	VET_ERROR_AllyTK_respString(_s)	)
		
	return list_error_found

def GET_1minCandle(symbol, requestRawData=True, **kwargs):
	# Public Client
	ratelimits.accessPublic()
	
	today = datetime.today().strftime('%Y-%m-%d')

	if Debug:
		today = '2018-03-28'

	return AllyTK.GET_MarketTimesales(symbol, startdate=today, requestRawData=requestRawData, **kwargs)

def GET_OptionNweekData(symbols, N, fids = AllyTK__SETTINGS.CONFIG_API['fids'], requestRawData=True, **kwargs):
	'''
		figureout the date of the next N+1 friday, then pick options before that.
		exmaple: query ='xmonth-gte:02ANDxdate-lte:20180302'
		exmaple: query ='xmonth-gte:02ANDxdate-lt:20180309' (3 weeks ahead, also doesn't mess with holiday closures if that becomes an issue)
		
		*AllyTK's API technically should avoid holiday on Friday's issue since you submit time interval, not difinitive dates
	'''
	# Public Client
	ratelimits.accessPublic()
	
	# Check number of Symbols
	if len(symbols) > AllyTK__SETTINGS.CONFIG_API['num_BatchSymbols']:
		raise ValueError("Number of symbols exceeded AllyTK__SETTINGS.CONFIG_API['num_BatchSymbols']")

	# 1) figureout the date of the next N+1 friday
	dmy_Fridaylist = MarketTimeManager.marketdatetime.dmy_nextNFridays(N+1)
	
	current_month = datetime(dmy_Fridaylist[0][2],dmy_Fridaylist[0][1],dmy_Fridaylist[0][0]).strftime('%m')
	last_friday = datetime(dmy_Fridaylist[N][2],dmy_Fridaylist[N][1],dmy_Fridaylist[N][0]).strftime('%Y%m%d')

	query='xmonth-gte:{}ANDxdate-lt:{}'.format(current_month,last_friday)

	return AllyTK.GET_MarketOptionsSearch(symbols, query = query, fids=fids, requestRawData=requestRawData)

if Debug:
	from threading import Thread
	init()
	
	starttime=time.time()
	list_symbols 	= ['AAPL','TSLA','AMZN','MSFT','GS','IBM']
	Nweeks			= 1
	'''
	for i in range(10):
		# Options
		_t1 = Thread(target=GET_OptionNweekData, args=[list_symbols,Nweeks])
		# Stocks
		_t2 = Thread(target=GET_OptionNweekData, args=[list_symbols,Nweeks])
		
		# start
		_t1.start()
		_t2.start()
		
		#join
		_t1.join()
		_t2.join()
		
		# GET_OptionNweekData(['AAPL','TSLA','AMZN','MSFT','GS','IBM'],2)
		
	print time.time()-starttime
	x=1
	'''
	_s = GET_OptionNweekData(list_symbols,2)
	# _s = GET_1minCandle(list_symbols[0])
	starttime=time.time()
	print VET_ERROR_AllyTK_respString(_s)
	print VET_ERROR_AllyTK_respString('badstr')
	print time.time()-starttime
	
	print PRECHECK_SymbolsList(list_symbols,2)