'''
	API written using OAuth for Ally(Trade King) api
	-j.freeman
	-recycling alot of haulan's eTrade code
	
	ALLY limits per minute not per second! we can grab all the minute candles at the beginning of the minute! 
	
	https://www.ally.com/api/invest/documentation/oauth/
	Apparently a static token is provided already for personal applications - protect it!
	Only distributable applications require the Oauth endpoints
	
	interestingly:
	-XML requests only, make a quick dict to XML payload function
	-JSON or XML responses! >> obviously use JSON parser, MVP plus faster to parse
'''

# -*- coding: utf-8 -*-
import requests, json
from requests_oauthlib import OAuth1
import pickle

from utils import json_handle

# import client settings
from config import AllyTK__SETTINGS
from utils import OAuth1_handle


# *******Globals*************
Logged_IN = False

sandboxMode = AllyTK__SETTINGS.CONFIG_UR1['sandboxMode']
OAuth1Credentials = OAuth1_handle.OAuth1Session(AllyTK__SETTINGS.CONFIG_UR3)

Debug = False
if Debug:
	from toolkit import speedtest
# ***************************

def rest_root():
	'''
		returns string representing root url which all requests are made
		'{}' sets places where other strings are to be inserted
	'''
	return 'https://api.tradeking.com/v1/{}.json'
	
def stream_root():
	'''
		upto 256 streaming updates! Great for
		https://www.ally.com/api/invest/documentation/streaming-market-quotes-get-post/
	'''
	return 'https://stream.tradeking.com/v1/{}.json'

def ConvertPayload2FIXML(payload):
	'''
		https://www.ally.com/api/invest/documentation/request-structure/
		Must convert dict payload into FIXML compliant where necessary
	'''
	# TBD when needed
	xml = payload
	return xml

def login():
	
	if OAuth1Credentials.sessionType=='STATIC':
		print'Access tokens found, AllyTK API to boot using static client'
		''' TBD
			Get account info
				if not successful
					print'AllyTK static tokens either dead, or bad connection'
		'''
	
	elif OAuth1Credentials.sessionType=='DYNAMIC':
		access_token_loaded = OAuth1Credentials.load_session()
		if access_token_loaded:
			print'Previous dynamic access tokens found, attempting to test them...'
		else:
			print'Dynamic access tokens not found, attempting to login...'
			# TBD when needed, complex mechanized browser to grab verification login code and tokens
		
		''' TBD to test tokens
			Get account info
				if successful
					print'AllyTK tokens verified'
				else
					print'Access rejected, attempting automated login...'
					funct_automated loging_getNewTokens()
		'''

	global Logged_IN
	Logged_IN = True
	
	print'Logged into AllyTK'
	
def accessMethod(url, method = 'GET', payload ={}, params ={}, requestRawData=False, *args, **kwargs):
	"""
	Adapted from Hualan's lib
	
	This is a generic function that calls for url <str> and method <'GET' or 'POST'>. If using 'POST', a payload <dict> should be supplied
	function returns a dict containing the output of the url called.
	
	http://docs.python-requests.org/en/latest/api/#main-interface
	request XML: https://stackoverflow.com/questions/12509888/how-can-i-send-an-xml-body-using-requests-library
	"""
	# convert payload to FIXML
	if (not payload=={}) and method=='POST':
		payload = ConvertPayload2FIXML(payload)
	
	''' OBSOLETE
	# Grab token if needed
	if USER.sessionType=='STATIC':
		resource_owner_token = USER.client_Token
		resource_owner_token_secret = USER.client_Token_Secret
	
	elif USER.sessionType=='DYNAMIC':
		try:
			user_tokens = pickle.load( open( 'AllyTK_user_tokens.p', "rb" ) )
			
			resource_owner_token = USER.client_Token = user_tokens['oauth_token']
			resource_owner_token_secret = USER.client_Token_Secret = user_tokens['oauth_token_secret']

		except IOError:
			# if the token file does not exist, it should be created
			return {'Error': 'AllyTK_user_tokens.p file missing'}
	
	# print user_tokens, client_Consumer_Key, client_Consumer_Secret
	# print url
	'''
	
	oauth = OAuth1(	client_key 				= OAuth1Credentials.client_Consumer_Key,
					client_secret			= OAuth1Credentials.client_Consumer_Secret,
					resource_owner_key		= OAuth1Credentials.client_Token, # = resource_owner_token
					resource_owner_secret	= OAuth1Credentials.client_Token_Secret # = resource_owner_token_secret 
	)
	
	try:
		if method == 'GET':
			r = requests.get(url = url, auth=oauth, params = params)
			
		elif method == 'POST':
			headers = {'Content-Type': 'application/json'}
			r = requests.post(url = url, auth=oauth, data = payload, headers = headers)
	
		else:
			raise "Invalid method: {}, please use only 'GET' or 'POST'".format()
	
		# HANDLING THE RESULT
		response = r.content
	
	except:
		# Something happened during request
		print'AllyTK low-level request error detected'
		response = '{"Error":"AllyTK low-level request error"}'
	
	if Debug:
		# Content is string object
		print 'DEBUG response:', response #j.freeman test

		
	# Check for errors from server and respond
	'''
		1) quick check for the word error in string without parsing
		2) if 'error' word found, continue to parse and do final check for error state
	'''
	
	# Run Checks if logged in and program running, response handled differently when not logged in
	# 	(when not logged in, you want to check if error returned in parent function)
	if Logged_IN:
	
		# 1) Quick Error Check
		if json_handle.CHECK_quickError(response):
	
			# 2) parse and do in-depth error check		
			response = ChecknHandle_ServerErrors(response)
		
	if requestRawData:
		return response
	else:
		return json_handle.parse_json2dict(response)

def ChecknHandle_ServerErrors(input):
	'''
		input is string response object > convert to _dict_ first
		AllyTK has a few hick-ups that need to be dealt with
	'''
	
	try:
		# Convert to dict
		_dict = json_handle.parse_json2dict(input)
		
		# Get Error message
		if 'error' in _dict['response']:
			msg_error = _dict['response']['error']
			
		elif 'message' in _dict['response']:
			msg_error = _dict['response']['message']
		
	except:
		msg_error='Quick_Error raised, but unable to locate error _dict_'
		pass
		
	if msg_error=='Success' or msg_error =='success':
		# Clean _dict
		return input
	
	else:
		print '\nError in Response:', input
		
	""" eTrade specific
	if Error['message'] =='oauth_problem=token_rejected':
		return "{'Error':'Login'}"
		'''
		# Solution: login again
		print'Token issue, Simulating fake panic, login and renew token again'
		HumanCondition(10,30)
		global Logged_IN
		Logged_IN = False
		login()
		'''
	"""
	
	# As of new method, return string, this will later be converted if need be
	return input

# *********ACCOUNT INFO*************************************************
def GET_UtilityStatus(*args, **kwargs):
	'''
		Returns time stamp if system is working
	'''
	url = rest_root().format('utility/status')
	return accessMethod(url, method = 'GET', *args, **kwargs)

def GET_Accounts(*args, **kwargs):
	'''
		Grabs all account information
	'''
	url = rest_root().format('accounts')
	
	return accessMethod(url, method = 'GET', *args, **kwargs)
	
def GET_Profile(*args, **kwargs):
	'''
		Grabs profile information
		https://www.ally.com/api/invest/documentation/member-profile-get/
	'''
	url = rest_root().format('member/profile')
	
	return accessMethod(url, method = 'GET', *args, **kwargs)
	
# ************MARKET DATA**************************************************************
def GET_MarketQuotes(symbols, *args, **kwargs):
	'''
		takes list of symbols, returns response
	'''
	if type(symbols)==type('str'):
		symbols = [symbols]

	str_symbols = ','.join(symbols)
	
	url = rest_root().format('market/ext/quotes') + '?' + \
	'symbols={}'.format(str_symbols)
	
	return accessMethod(url, method = 'GET', *args, **kwargs)

def GET_MarketTimesales(symbols,
						interval='1min',
						rpp = '',
						index = '',
						startdate = '',
						enddate = '',
						starttime = '',
						*args, **kwargs):
	'''
		Takes a SINGLE symbol and returns candles
		if you add more than 1 symbol, it only returns the first
	'''
	if type(symbols)==type('str'):
		symbols = [symbols]
	
	if startdate =='':
		print'Warning: startdate parameter required'
		return

	url = rest_root().format('market/timesales')

	'''
	str_symbols = ','.join(symbols)
	+ '?' + \
	'symbols={}'.format(str_symbols) + '&' + \
	'startdate={}'.format(startdate) + '&' + \
	'interval={}'.format(interval)
	
	if not rpp == None:
		url += ('&' + 'rpp={}'.format(rpp))
		
	if not index == None:
		url += ('&' + 'index={}'.format(index))
		
	if (not enddate == None) and (not enddate == startdate):
		url += ('&' + 'enddate={}'.format(enddate))
	
	if not starttime == '':
		url += ('&' + 'starttime={}'.format(starttime))
	'''
	
	params = {
		'symbols' : ','.join(symbols),
		'startdate' : startdate,
		'interval' : interval,
		'starttime':starttime,
		'rpp' : rpp,
		'index' : index,
		'enddate' : enddate
	}

	return accessMethod(url, method = 'GET', params = params, *args, **kwargs)

def GET_MarketOptionsSearch(symbols,
							query = '',
							fids = [''],
							*args, **kwargs):
	'''
		https://www.ally.com/api/invest/documentation/market-options-search-get-post/
	'''
	if type(symbols)==type('str'):
		symbols = [symbols]
	
	url = rest_root().format('market/options/search')

	'''
		to get Nweek data use the current xmonth as low, and Nth week's xdate bounds
		exmaple: query ='xmonth-gte:02ANDxdate-lte:20180302'
	'''
	if query == '':
		# test query
		query ='xyear-gte:2018'
		print('Warning: query undefined, resorting to default test query: ',query)
	
	params = {
		'symbol' : ','.join(symbols),
		'query' : query,
		'fids' : ','.join(fids)
	}
	return accessMethod(url, method = 'GET', params = params, *args, **kwargs)

"""
# *******STREAMING API below********************************************************************
def GET_MarketStream(symbols):
	'''
		Starts a stream
	'''
	str_symbols = ','.join(symbols)
	
	url = stream_root().format('market/quotes')
	
	params = {
		'symbols': ','.join(symbols)
	}
	read_stream(url, method = 'GET', params=params)
	
def accessStream(url, method = 'GET', payload={}, params={}, headers={}):
	'''
		https://stackoverflow.com/questions/17822342/understanding-python-http-streaming
	'''
	s = requests.Session()

	if headers =={}:
		# Default stream headers
		headers = {'connection': 'keep-alive', 'content-type': 'application/json', 'x-powered-by': 'Express', 'transfer-encoding': 'chunked'}
	
	resource_owner_token = None
	resource_owner_token_secret = None

	# Grab token if needed
	if USER.sessionType=='STATIC':
		resource_owner_token = USER.client_Token
		resource_owner_token_secret = USER.client_Token_Secret
	
	elif USER.sessionType=='DYNAMIC':
		try:
			user_tokens = pickle.load( open( 'AllyTK_user_tokens.p', "rb" ) )
			
			resource_owner_token = USER.client_Token = user_tokens['oauth_token']
			resource_owner_token_secret = USER.client_Token_Secret = user_tokens['oauth_token_secret']

		except IOError:
			# if the token file does not exist, it should be created
			#return {Error': 'AllyTK_user_tokens.p file missing'} doesn't work with generator
			print 'AllyTK_user_tokens.p file missing'
			pass
	
	if method == 'GET':
		oauth = OAuth1(	client_key 			= USER.client_Consumer_Key,
						client_secret		= USER.client_Consumer_Secret,
						resource_owner_key	= resource_owner_token,
						resource_owner_secret=resource_owner_token_secret
		)
		print 'here'
		req = requests.Request("GET",url,
						   headers = headers,
						   params = params,
						   auth=oauth).prepare()

	resp = s.send(req, stream=True)
	print 'here'
	for line in resp.iter_lines():
		'''
			https://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do#231855
		'''
		print 'here'
		if line:
			yield line

def read_stream(url, **kwargs):
	print url
	for line in accessStream(url, **kwargs):
		# accessStream is an generator that spits out iterable values, so the current tread hangs as it waits for objects 
		print line
		# ultimately you would want to put this on a pipeOUT to a main thread to use. 

#GET_MarketStream(['AAPL','AMZN'])


'''
with open('test.txt','w') as outfile:
	pageObj = GET_MarketStream(['AAPL'])
	json.dump(pageObj, outfile, default=lambda o: o.__dict__)
	outfile.write('\n')
'''

# *******STREAMING API above********************************************************************
"""

if Debug:
	login()
	print GET_MarketQuotes(['AAPL','AMZN'], requestRawData=True)
	print GET_UtilityStatus()