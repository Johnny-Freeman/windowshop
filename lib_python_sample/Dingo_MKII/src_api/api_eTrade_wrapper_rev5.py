'''
	API wrapper for eTrade api
	This is needed to standardize all the function calls being called
	
	* as of Rev5, all GET_MarketData functions will be converted to return raw string objects, GET_account data will still be parsed
'''
import string, json, os, re

from utils import marketTime as MarketTimeManager
from utils import list_management
from utils.framework import pyclass

import api_eTrade_rev4 as etrade
from classes import Datastore_OptionExpirationDates
from classes import API_Thresholds

# *******START****eTrade Globals*************
from config import eTrade__SETTINGS
ratelimits = API_Thresholds.RateLimits('ETRADE', eTrade__SETTINGS.CONFIG_API)

accountList = [None]
StrikePriceStore = Datastore_OptionExpirationDates.StrikePriceStoreManager()

Debug = False
# *********END****eTrade Globals*************

def login():
	# Private Client - track API rate limits
	ratelimits.accessPrivate()
	
	etrade.login()
	# Get account numbers as array currently designed only to use one account number to speed things up
	global accountList
	accountList = GET_accountList()
	
	print'Reminder to run LOAD_ExpirationDates(symbol,N)'

# account related functions **********************************
def GET_accountList():
	# Private Client - track API rate limits
	ratelimits.accessPrivate()
	
	if not accountList == [None]:
		'''
			This only works with one one Oauth running, will need to be revisited later
				(later) make it call on various usernames
		'''
		return accountList

	#if Debug:
	#	return [83405188]
	
	eTradeAccounts = []

	# If eTrade API gets fixed, write funct
	pagedict = etrade.listAccounts()
	#print pagedict

	# Annoying dict block on eTrade workaround
	element = pagedict["json.accountListResponse"]
	element = pyclass.importDict_Xeye(element).response
	#print element
	
	# Grab account numbers from array
	for i in range(len(element)):
		eTradeAccounts.append(element[i].accountId)

	return eTradeAccounts
	
def GET_orderList(accountnum=None):
	'''
		Hualan's API does a pretty good job combining if more than 25 orders already!
		RETURNS list of dicts, each individual order
	'''
	# Private Client - track API rate limits
	ratelimits.accessPrivate()
	
	accountnum= accountList[0]
	
	resp_dictList = etrade.listOrders(accountnum)
	
	if resp_dictList == None:
		return None

	resp_objList = []	
	for i in range(len(resp_dictList)):
		resp_objList.append(pyclass.importDict_Xeye(resp_dictList[i]))

	return resp_objList

def POST_cancelOrder(accountnum=None, orderId=None):
	'''
		simple wrapper
	'''
	# Private Client - track API rate limits
	ratelimits.accessPrivate()
	
	accountnum= accountList[0]
	
	pagedict = etrade.cancelOrder(accountnum, orderId)
	return pyclass.importDict_Xeye(pagedict)
	
def GET_accountBalances(accountnum=None):
	'''
		https://us.etrade.com/ctnt/dev-portal/getDetail?contentUri=V0_Documentation-AccountsAPI-GetAccountBalance
		Values of trading interest: fundsWithheldFromPurchasePower, totalcash, totalLongValue

		netcash(a maxlimit for order_manager.py) = totalcash - fundsWithheldFromPurchasePower (some money withheld for LT stock crash catches)
		Bankroll(totalActive portforlio value)= totalcash + totalLongValue
	'''
	# Private Client - track API rate limits
	ratelimits.accessPrivate()
	
	accountnum= accountList[0]
	
	pagedict = etrade.getAccountBalance(accountnum)
	return

def GET_accountPositions(accountnum=None):
	'''
		Goal is to be able to update the main_manager.py loop so if new options are opened up by user, they will also be tracked
		may even be done later, and instead for now ignore and stick with entering orders through python only!
	'''
	accountnum= accountList[0]
	
	pagedict = getAccountPositions(accountnum)
	return

# STOCK related functions **************************************
'''
	GET_MarketData functions now handle all rawData as strings, WITHOUT parsing
	Parsing will now be handled by End-user for Data functions since it adds CPU overhead on large objects
'''

def GET_singleQuote(tick, detailFlag = 'ALL'):
	# Public Client - track API rate limits
	ratelimits.accessPublic()
	
	# pagedict = etrade.getQuote(tick, detailFlag)
	# return pyclass.importDict_Xeye(pagedict)
	return etrade.getQuote(tick, detailFlag, requestRawData=True)
	
def POST_BUY_Stock(orderAction='BUY', priceType='MARKET', *args, **kwargs):
	'''
		EXMAPLE USEAGE:
		POST_BUY_Stock(
						AcctNumber =,
						symbol=,
						quantity=,
						orderAction='BUY',
						priceType='MARKET',
						limitPrice = None,
						*args, **kwargs):
	'''
	# Private Client - track API rate limits
	ratelimits.accessPrivate()

	#Passing on **kwargs
	kwargs['AcctNumber'] = accountList[0]	#MVP1
	kwargs['orderAction'] = orderAction
	kwargs['priceType'] = priceType

	params = etrade.previewEquityOrder(sendPost=False, *args, **kwargs)
	
	resp_dict = etrade.placeEquityOrder(params)
	return pyclass.importDict_Xeye(resp_dict)

def POST_SELL_Stock(orderAction='SELL', priceType='MARKET', *args, **kwargs):
	'''
		EXMAPLE USEAGE:
		POST_SELL_Stock(
						AcctNumber =,
						symbol=,
						quantity=,
						orderAction='SELL',
						priceType='MARKET',
						limitPrice = None,
						*args, **kwargs):
	'''
	# Private Client - track API rate limits
	ratelimits.accessPrivate()

	#Passing on **kwargs
	kwargs['AcctNumber'] = accountList[0]	#MVP1
	kwargs['orderAction'] = orderAction
	kwargs['priceType'] = priceType


	params = etrade.previewEquityOrder(sendPost=False, *args, **kwargs)
	
	resp_dict = etrade.placeEquityOrder(params)
	return pyclass.importDict_Xeye(resp_dict)

# OPTION related functions **************************************
def GET_singleOptionQuote(symbol, detailFlag = 'OPTIONS'):
	# Public Client - tracking API usage
	ratelimits.accessPublic()
	
	# pagedict = etrade.getQuote(symbol, detailFlag)
	# return pyclass.importDict_Xeye(pagedict)
	return etrade.getQuote(symbol, detailFlag, requestRawData=True)

def POST_BUY_Options(orderAction='BUY_OPEN', priceType='LIMIT', *args, **kwargs):
	'''
		SymbolInfoList = ['IBM','CALL/PUT', <strikePrice>, <expYear>, <expMonth>, <expDay>]
		priceType = Limit by default, but it really should be dictated by ordering algo for execution
		, for the most part limit since we have to be careful of being wiped out
		
		EXAMPLE USAGE
		POST_BUY_Options(						# PASSED following as **kwargs __dict__
						AcctNumber=,			# REQUIRED: Left out of MVP1, assume just one main account
						SymbolInfoList=,		# REQUIRED: ['IBM','CALL',115,2010,4,17] , [<Ticker>, <CALL/PUT>, <Strike>, <Year>, <Month>, <Day>]
						orderAction=,			# PRESET: already define as BUY or SELL by function
						quantity=,				# REQUIRED: Size of order
						priceType = None, 		# REQUIRED: LIMIT or MARKET, LIMIT by DEFAULT
						limitPrice = None, 		# REQUIRED BY priceType = LIMIT: max you would pay to purchase
						
						# Below kwargs rarely used
						stopPrice = None,
						allOrNone = False,
						reserveOrder = False, 
						reserveQuantity = None, 
						marketSession = 'REGULAR',
						orderTerm = 'GOOD_FOR_DAY',
						routingDestination = 'AUTO',
						sendPost=False,			# PRESET: defined by wrapper and API, no need to worry as called function (retrieves preview of order, waste of time)
						clientOrderId = None,
						*args,**kwargs):
	'''
	# Private Client - track API rate limits
	ratelimits.accessPrivate()
	
	#Passing on **kwargs
	kwargs['AcctNumber'] = accountList[0]	#MVP1
	kwargs['orderAction'] = orderAction
	kwargs['priceType'] = priceType

	params = etrade.previewOptionOrder(sendPost=False, *args, **kwargs)
	
	resp_dict = etrade.placeOptionOrder(params)
	return pyclass.importDict_Xeye(resp_dict)

def POST_SELL_Options(orderAction='SELL_CLOSE', priceType='LIMIT', *args, **kwargs):
	# Private Client - track API rate limits
	ratelimits.accessPrivate()
	
	#Passing on **kwargs
	kwargs['AcctNumber'] = accountList[0]
	kwargs['orderAction'] = orderAction
	kwargs['priceType'] = priceType

	params = etrade.previewOptionOrder(sendPost=False, *args, **kwargs)
	
	resp_dict = etrade.placeOptionOrder(params)
	return pyclass.importDict_Xeye(resp_dict)
	
def GET_OptionExpireDates(symbol):
	# Public Client - track API usage
	ratelimits.accessPublic()
	
	# page = etrade.getOptionExpireDate(symbol)
	# return pyclass.importDict_Xeye(page)
	return etrade.getOptionExpireDate(symbol, requestRawData=True)
	
def GET_obj_OptionChains(symbol, daymonthyears, chainType='CALLPUT', skipAdjusted=True):
	'''
		Returns:
		class importDict_Xeye() {
			self.optionChainResponse.optionPairCount
			self.optionChainResponse.optionPairs
			+ lots of accessory data
		}
		
		Returns concat ResponseObjectWebPage containing of full range of option_chains for given list of <daymonthyears>
		Data integrity provided by VET_GET_singleOptionChain
		
		Grab's the current month's options, and if more than one monthyear, the next months, then concatenates
		daymonthyears = [[26,01,2017],[26,02,2017],...]
	'''
	pageobj = None
	for i in range(len(daymonthyears)):
		if i == 0:
			# first instance
			pageobj = VET_GET_singleOptionChain(symbol, daymonthyears[0], chainType, skipAdjusted)
			
		else:
			# if more than one start concat
			newobj = VET_GET_singleOptionChain(symbol, daymonthyears[i], chainType, skipAdjusted)

			pageobj.optionChainResponse.optionPairCount += newobj.optionChainResponse.optionPairCount
			pageobj.optionChainResponse.optionPairs += newobj.optionChainResponse.optionPairs

	return pageobj
	
def VET_GET_singleOptionChain(*args, **kwargs):
	'''
		Converts singleOptionChain stringObject into class instance and verifies data integrity
		
		* This should also be called independently at beginning to verify individual expiration dates
			, such as holidays and other sneaky market_maker changes to mess up algos
	'''
	
	ResponseObject = pyclass.string2Object(	GET_singleOptionChain(*args, **kwargs)	)
	
	# Data integrity check
	'''
		Raises error (Intentionally) if unable to verify data integrity
			>> this will be handled as indicator that current option chain expiration data is wrong or not found (Likely due to market makers changing the expiration format)
	'''
	try:
		ResponseObject.optionChainResponse.optionPairCount
		ResponseObject.optionChainResponse.optionPairs
		return ResponseObject
	except:
		symbol = args[0]
		daymonthyear = args[1]

		print ('Issue grabbing OptionChain for: ' + symbol + ' ' + str(daymonthyear)	)
		raise ValueError('Bad Data, GET_singleOptionChain')
	
def GET_singleOptionChain(symbol, daymonthyear, chainType='CALLPUT', skipAdjusted=True):
	'''
		daymonthyear = [26,01,2018]
	'''
	# Public Client - track API-usage
	ratelimits.accessPublic()
	
	day = daymonthyear[0]
	month = daymonthyear[1]
	year = daymonthyear[2]
	# Get single month's option chain
	# page = etrade.getOptionChains(chainType, day, month, year, symbol, skipAdjusted)
	# return pyclass.importDict_Xeye(page)
	return etrade.getOptionChains(chainType, day, month, year, symbol, skipAdjusted, requestRawData=True)

def GRAB_StrikeListfromOptionChain(pageobj, daymonthyear, start=None):
	'''
		Returns single list of strike prices:
		<daymonthyear> [10,20,30,40,...] << for a single daymonthyear(Friday)
	
		Scans pageobj and returns a single list of strike prices
			, and if a start index is specified will begin screen at the starting index [0 count] - also returns ending index
			, if no start index, starts at zero, and does not return ending index
				, using start index assumes ordered list is in order
		
		one interesting thing with python is even though we "pass" in pageobj
			, pageobj points to the initiating object! thus saving memory
			, only when a new object created is new memory used. Dispite not having pointers
	'''
	strikelist = []
	if start == None:
		startidx = 0
	else:
		startidx = start
	
	# see optionchain response for format
	maxcount = pageobj.optionChainResponse.optionPairCount
	end = startidx
	negbuffer = 15	#number of continuous negative scans
	
	for i in range(startidx,maxcount):
		# For each ordered pair check if day matches daymonthyear
		if pageobj.optionChainResponse.optionPairs[i].put.expireDate.day == daymonthyear[0]:
		
			# If yes, increase the end index and append strike value to list
			
			# DEBUG: print pageobj.optionChainResponse.optionPairs[i].put.strikePrice
			strikelist.append(pageobj.optionChainResponse.optionPairs[i].put.strikePrice)
			end = i
			negbuffer = 15 # reset
		
		# countdown buffer
		else:
			negbuffer -=1
			if negbuffer==0:
				break
	
	# return list or both list and ending index
	if start ==None:
		return strikelist
	else:
		return strikelist, end

def GET_StrikeChart_fromChain_byWeek(symbol, dmy_Fridays):
	'''
		Returns a strike chart:
		[
			<Friday #n=1> [10,20,30,40],	<<< list of strike prices for given dmy_Fridays[i=n]
			<Friday #n=2> [10,15,20,30],
			...
		]
		
		Generic function, takes a preferibly CHRONOLOICAL list of dmy_Friday's
		1) Get Optionchain response for list of Fridays, (serial object)
		2) loops through them to compile a chart of strike prices in same order as dmy_Fridays
		3) returns chart[[],[],[]]
	'''
	# 1)
	respObj_optionchain = GET_obj_OptionChains(symbol, dmy_Fridays)
	
	# 2)
	strikechart = []
	idx = 0
	
	for i in range(len(dmy_Fridays)):
		#append the returned list to the strikechart
		strikelist, idx = GRAB_StrikeListfromOptionChain(respObj_optionchain, dmy_Fridays[i], idx)
		strikechart.append(strikelist)
	# 3)
	return strikechart

def CompileStrikePriceStore(symbol, N):
	'''
		Only updates available strike prices when needed.
		A) Does symbol exist in strikeliststore? NO> Grab all and append to store
		B) Sufficient number of weeks? NO > Grab rest of the weeks and append to store
	'''
	
	# A)
	if not StrikePriceStore.symbolstored(symbol):
		# create new instance of a strikelist
		'''
			newchart = Datastore_OptionExpirationDates.StrikePriceChart(symbol)
			StrikePriceStore[symbol] = newchart
		'''
		StrikePriceStore.NEW_StrikePriceChart(symbol)

	# To hold the starting index which weeks to grab
	#		, assumed, and designed to hold weeks in chronological order
	m = len(StrikePriceStore[symbol].strikechart)

	if m >= N:
		#no need to do anymore
		return True

	# Not necessary List of Fridays, but list of expiration dates, however this drive the point home since typically on a Friday
	dmy_Fridaylist = StrikePriceStore.GRAB_dmy_nextNExpirations(N)
	
	# Slice Front of Friday List off
	dmy_mNfridays = dmy_Fridaylist[m:]
	
	# get strike chart
	tempchart = GET_StrikeChart_fromChain_byWeek(symbol, dmy_mNfridays)
	
	# append to StrikePriceStore
	StrikePriceStore[symbol].strikechart += tempchart
	
def LOAD_ExpirationDates(symbol, N):
	'''
		1) Get list of N_weeks of dmy_friday's,
		2) Check each dmy_friday,
			if error returned,
				cycle through friday-1 (thursday), and so on until non error returned
		3) compile list of actual expiration dates
	'''
	# 1)
	list_dmyFridays = MarketTimeManager.marketdatetime.dmy_nextNFridays(N)
	
	# 2) Check each dmy_Friday
	list_NWeeks = []
	for i in range(N):
		k_minus = 0
		while(True):
			try:
				VET_GET_singleOptionChain(symbol,list_dmyFridays[i])
				list_NWeeks.append(list_dmyFridays[i])
				break
			except:
				k_minus +=1
				if k_minus > 4:
					# if day < monday, no need to get weekly options for this week, skip to next week
					break
				
				# dmy_Friday is of format [day,month,year]
				# Subtract one day, obviously no longer Friday, but this was pretty descriptive at the time
				list_dmyFridays[i] = MarketTimeManager.marketdatetime.dmy_prevDay(list_dmyFridays[i])
	
	StrikePriceStore.SET_nextNExpirations(list_NWeeks)
				
	print'Loaded OptionExpiration Dates: ', list_NWeeks

def PREcompileStrikePriceStore(symbol_list, N):
	'''
		Mainly to be used in an Init() function
		params([list of symbols you want option lists precombiled for], int#N of Weeks you want compiled)
		
		** really need to write list_fail to file as "today()_failed_weekly_options_lookup_list.txt"
			- would help to modify future options lists and lessen load on internet connection from attempting to grab dead options
	'''
	if len(symbol_list) == 0:
		print'Warning69: PREcompileStrikePriceStore( <symbol_list> ) not defined, unable to grab expiration dates, Rerun with options_list if interested in getting options data\n'
		return [],[]
	
	# Check to see if list is long enough
	try:
		StrikePriceStore.GRAB_dmy_nextNExpirations(N)
	except:
		LOAD_ExpirationDates(symbol_list[0],N)
	
	# Hold lists of what worked and didn't
	list_sucess=[]
	list_fail=[]

	for i in range(len(symbol_list)):
		try:
			CompileStrikePriceStore(symbol_list[i], N)
			list_sucess.append(symbol_list[i])
		except:
			print('Issue with getting weekly option chain for: ' + symbol_list[i])
			list_fail.append(symbol_list[i])
			pass
	
	return list_sucess, list_fail

def GET_Option_NweekStrikeList(symbol, N):
	'''
		Saves a Mirror of available strike prices for options
	
		1) Compile Store (main problem is throttle speed, thus we just need to store a cache for the day)
		2) Search Store for StrikeList
		
		1) Vertical Logic:
		A) Does symbol exist in strikeliststore? NO> Grab all and append to store
		B) Sufficient number of weeks? NO > Grab rest of the weeks and append to store	
	'''
	# 1) Compile
	# dmy_Fridaylist = 	MarketTimeManager.marketdatetime.dmy_nextNFridays(N) # line not actually needed!
	#					StrikePriceStore.GRAB_dmy_nextNExpirations(N)			<< More recent which checks Friday if it's a valid expiration date or not!
	#	- we assume the StrikePriceStore is Chronological starting with the 0th friday as this week, Nth_Friday returns list of strike prices

	CompileStrikePriceStore(symbol, N)

	# 2) Search Store, return slice(list of strike prices)
	return StrikePriceStore[symbol].strikechart[:N]


# General Batch functions ****************************************
def GET_25batch(ticks, detailFlag, requestRawData=True):
	'''
		ticks format = ['goog','tsla','fdx']
		returns eTrade's results which has buffer brackets {{, }} etc.
			- To be addressed in a wrapper function to this one to handle merging the response to mimic
		UPTO 25 quotes at a time
	'''
	# Public Client - Tracking API rate useage
	ratelimits.accessPublic()
	
	if len(ticks) > eTrade__SETTINGS.CONFIG_API['num_BatchSymbols']:
		raise ValueError('GET_25batch Quote only takes up to ' + str(eTrade__SETTINGS.CONFIG_API['num_BatchSymbols']) + ' tickers at once')
		return False
	
	str_ticks = ''
	for i in range(len(ticks)):
		str_ticks += ticks[i] + ','
	
	#remove last ',' instead of checking against length in loop
	str_ticks = str_ticks[:-1]
	
	return etrade.getQuote(str_ticks, detailFlag, requestRawData=requestRawData)
	
def ConvertFormat_tobatchString(respString):
	'''
		Takes Response string for what normally would be a single quote response and converts it into a batch like format
		This makes it easier down the line when the batch requested is only of length 1, we can standardize the format
		
		# Note extra [ , ] brackets
		single request	= {"quoteResponse":{"quoteData":{"all":{"adjNonAdjFlag":false,"annualDividend":2.52,"ask":166. ...  ... ":"AAPL","type":"EQ","exchange":"Q "}}}}
		multi request	= {"quoteResponse":{"quoteData": [ {"all":{"adjNonAdjFlag":false,"annualDividend":2.52,"ask":166 ... ... ","type":"EQ","exchange":"Q "}} ] }}
	'''
	
	# Method 2, using regular expressions
	'''
		https://stackoverflow.com/questions/4893506/fastest-python-method-for-search-and-replace-on-a-large-string#4893549
	'''
	''' Robust But 1 magnitude slower (Actually tested in self contained test)
	reg_front = re.compile(r'("quoteData":{"all")')
	reg_back = re.compile(r'(}}}})')
	
	rep_front = '"quoteData":[{"all"'
	rep_back = '}}]}}'
	
	output = re.sub(reg, rep, text)
	'''
	
	# Method 1, literally counting index position
	loc_first = 30
	loc_last = -2
	
	front = respString[:loc_first]
	center = respString[loc_first:loc_last]
	back = respString[loc_last:]
	
	return(front + '[' + center + ']' + back)

def Get_25batchString(ticks, detailFlag, requestRawData=True):
	'''
		Retrieves dict quotes from eTrade up to eTrade's batch limit(25)
		Since we are dealing with 1 or many batch sizes
			, here we standardize the object format to batch-like when calling the batch functions, versus single quote calls
	'''
	# Retrieve dict
	string_page = GET_25batch(ticks, detailFlag, requestRawData=True)
	
	# Tick length 1 exception
	if len(ticks) == 1:
		string_page = ConvertFormat_tobatchString(string_page)
		
	return string_page
	
def VETCONCAT_eTrade_respStrings(list_respString):
	'''	An accessory function that does two things
		1 ) Verifies Data integrity
		2 ) CONCATS list of response data according to eTrade standard (multi/single quote)

		# Note extra [ , ] brackets
		multi_request	= {"quoteResponse":{"quoteData": [ {"all":{"adjNonAdjFlag":false,"annualDividend":2.52,"ask":166 ... ... ","type":"EQ","exchange":"Q "}} ] }}
	
		Will return empty responses if error check fails
		
		{"quoteResponse":{"quoteData":[   <failed>   ]}}
		{"quoteResponse":{"quoteData":[   {DATA},<failed(no comma)>, {DATA}   ]}}
	'''
	# Rare for these to change, unless eTrade updates their API
	FrontBlock	= '{"quoteResponse":{"quoteData":['
	RearBlock	= ']}}'
	
	# Strings to test data quality, reject string if fails
	test_frontData	='{"'
	test_rearData	='}}'
	
	# Method 1, literally counting index position (uses direct index lookup)
	# Intra-Bracket locations [1,2,3 ,..... ,-3,-2,-1]
	loc_first = 31
	loc_last = -3
	
	list_editString = []
	N_length = len(list_respString)
	
	error_found = False
	for i in range(N_length):
		# Main bit of Data
		if not (list_respString[i] == None):
			edited_string = list_respString[i][loc_first:loc_last]
		else:
			edited_string = '{"error":"Request timed out"}'
		
		# Test strings to make sure no errors in data
		if (edited_string[:2] == test_frontData) and (edited_string[-2:]==test_rearData):
			list_editString.append(edited_string)
		else:
			error_found = True
	
	# Error fixed ''.join > ','join > json failed to parse properly without delimiter
	return(FrontBlock + ','.join(list_editString) + RearBlock, error_found)
	
# ****************** Depreciated Class_object styled functions ****in favor of handling as raw string to limit CPU resources*****************
def ConvertFormat_tobatchObject(pageobj):
	'''
		To standardize the batch function to include the length of 1 exception
		Generate list of length 1 and replace in obj
		
		* For the most part no longer used in favor of 
	'''
	
	# Generate list of length 1 (key = .quoteData)
	quotedat = [pageobj.quoteResponse.quoteData]
	
	# replace
	pageobj.quoteResponse.quoteData = quotedat
	
	return pageobj	

def Get_25batchObject(ticks, detailFlag, requestRawData=False):
	'''
		Retrieves dict quotes from eTrade up to eTrade's batch limit(25)
		Since we are dealing with 1 or many batch sizes
			, here we standardize the object format to batch-like when calling the batch functions, versus single quote calls
	'''
	# Retrieve dict
	dict_page = GET_25batch(ticks, detailFlag, requestRawData=False)
	
	# Convert dict to object class
	pageobj = pyclass.importDict_Xeye(str_page)
	
	# Tick length 1 exception
	if len(ticks) == 1:
		pageobj = ConvertFormat_tobatchObject(pageobj)
		
	return pageobj