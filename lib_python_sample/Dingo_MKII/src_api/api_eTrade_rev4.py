'''
	Modified eTrade Python API to support rawData string calls on-demand
		(solves issue of parsing and dumping large data objects when writing them, this used up a lot of cpu)
		also easier to pass string later down the line into multiprocess to handle parsing.
		
	Oauth1 session now stored and referenced from memory to remove need to open and read from file everytime a request is made
		leading to additional improvement on io-collisions
	
	* WEB app provided by eTrade
	* original code by Hualan
	**Heavily modified by j.freeman 2018
'''

# -*- coding: utf-8 -*-
import requests, json
from requests_oauthlib import OAuth1 , OAuth1Session
import pickle, webbrowser, random, string, time, os, sys
from pprint import pprint

# For automated logins
if os.name =='nt':
	import mechanize, re
elif os.name =='posix':
	from splinter import Browser
	from pyvirtualdisplay import Display
	
from utils.framework import HumanCondition
from utils import json_handle

"""
This is an attempt to implement a python compatible version of the etrade API using the `requests` library
"""
# import client settings
from config import eTrade__SETTINGS
from utils import OAuth1_handle

# ***********Globals***************************
Logged_IN = False
sandboxMode = eTrade__SETTINGS.CONFIG_ETRADE['sandboxMode']

# Readability
OAuth1Credentials = OAuth1_handle.OAuth1Session(eTrade__SETTINGS.CONFIG_ETRADE)
client_Consumer_Key = OAuth1Credentials.client_Consumer_Key
client_Consumer_Secret = OAuth1Credentials.client_Consumer_Secret

Debug = False
if Debug:
	from toolkit import speedtest

# ***********END Globals***********************

def urlRoot():
	"""
	returns the root URL for the etrade API depending on sandboxMode <boolean>
	"""

	if sandboxMode:
		return 'https://etwssandbox.etrade.com/{}/sandbox/rest/{}.json'
	else:
		return 'https://etws.etrade.com/{}/rest/{}.json'

def getRequestToken():
	"""
	Returns a dict containing a pair of temporary token and secret

	"""
	request_token_url = '{}/{}/{}'.format('https://etws.etrade.com','oauth','request_token')
	oauth = OAuth1Session(	client_key=client_Consumer_Key, 
							client_secret=client_Consumer_Secret,
							callback_uri='oob')

	fetch_response = oauth.fetch_request_token(request_token_url)
	# resource_owner_key = fetch_response['oauth_token']
	# resource_owner_secret = fetch_response['oauth_token_secret']
 

	return fetch_response

def authorizeToken(requestTokenResponse):
	'''
		Retrieves oAuth code from eTrade to be returned:
		1) Detects OS and
		2) attempts to run corresponding autologin
		3) If auto login fails > run login screen
	'''
	authCode=None

	num_try = 0
	# Keep trying to login until proper answer given
	while num_try < 5:
		try:
			os_name = os.name
			if os_name =='nt':
				print'Windows detected, attempting Windows AutoLogin, try: ',num_try
				authCode= authorizeToke_Windows_autologin(requestTokenResponse)
			elif os_name =='posix':
				print'Linux detected, attempting Linux AutoLogin (requires Splinter and pyvirtualdisplay), try: ',num_try
				authCode= authorizeToken_Linux_autologin(requestTokenResponse)

			return authCode
		
		except Exception as e:
			print('PyException: '+str(e))
			time.sleep(30)
			num_try+=1
			pass
	
	try:
		print'Final Auto-Attempt: Mechnized AutoLogin regardless of system'
		authCode= authorizeToke_Windows_autologin(requestTokenResponse)
	except Exception as e:
		print('PyException: '+str(e))
		pass
	
	try:
		print'AutoLogin has failed, attempting manual override...'
		authCode= authorizeToken_manual(requestTokenResponse)
	except Exception as e:
		print('PyException: '+str(e))
		raw_input('Manual login has failed, debug and restart program')

	return authCode

def authorizeToke_Windows_autologin(requestTokenResponse):
	'''
		Using Mechanize and Regular expressions to automate getting oauth code
			Also adding in human condition to make it look like human at the keys
	'''

	resource_owner_key = requestTokenResponse['oauth_token']
	resource_owner_secret = requestTokenResponse['oauth_token_secret']
	redirect_response = 'https://us.etrade.com/e/t/etws/authorize?key={}&token={}'.format(client_Consumer_Key,resource_owner_key)
	

	
	url = redirect_response
	
	# HTTP response = Browser window.action
	br = mechanize.Browser()
	br.open(url)
	
	# 'Tab_Window' like attributes
	assert br.viewing_html()
	print br.title()
	
	# Human Condition
	print'Simulating Typing Credentials'
	HumanCondition.HumanCondition(7,10)
	
	# Tunnel through html to desired forms
	br.select_form(name='log-on-form')
	br['USER'] = OAuth1Credentials.username
	br['PASSWORD'] = OAuth1Credentials.userpass
	br.submit()
	
	# Human Condition
	print'Logged in... accepting random conditions'
	HumanCondition.HumanCondition(4,6)
	
	# Now lets press the accept button
	# , with eTrade looks like they have two submit buttons
	# <form name="CustInfo" method="post" action="/e/t/etws/TradingAPICustomerInfo">
	# 1-<input NAME="submit" TYPE="submit" VALUE="Accept">
	# 2-<input NAME="submit" TYPE="submit" VALUE="Decline">
	br.select_form(name='CustInfo')
	resp = br.submit(name='submit', label='Accept')
	
	# Grab Verification Code, uses regular expressions(re)
	str_resp = resp.get_data()
	
	''' Regular expression for '<input TYPE="text" VALUE="H7ASF' and some random white space character at the end
		<input TYPE="text" VALUE="
		\w{5,5} match exactly 5 alphanumeric 
		
		https://docs.python.org/2/library/re.html
	'''
	pattern = re.compile('TYPE="text" VALUE="\w{5,5}')
	match = re.findall(pattern, str_resp)
	if not len(match) ==1:
		print'Something wrong occured during Regular Expression parse'

	authCode = match[0]
	authCode = authCode[-5:]
	
	# Human Condition
	print'Accepted, verfication code: ',authCode
	print'Simulating copy and paste...'
	HumanCondition.HumanCondition(5,8)
	print'Program starting\n'
	
	return authCode

def authorizeToken_Linux_autologin(requestTokenResponse):
	"""
	Given a dict requestTokenResponse with the temporary oauth_token and oauth_token_secret,
	we generate a login link that a user should interact with to obtain an authCode <str>
	This process is automated with Splinter and pyvirtualdisplay
	"""

	resource_owner_key = requestTokenResponse['oauth_token']
	resource_owner_secret = requestTokenResponse['oauth_token_secret']
	redirect_response = 'https://us.etrade.com/e/t/etws/authorize?key={}&token={}'.format(client_Consumer_Key,resource_owner_key)
	

	# print 'go to this link for authorization:', redirect_response

	# cannot parse redirect_response without a browser because the response is not pure json
	# oauth_response = oauth.parse_authorization_response(redirect_response)

	# Open URL in a new tab, if a browser window is already open.
	# webbrowser.open_new_tab(redirect_response)

	# Display allows the script to run in a linux cloud without a screen
	display = Display(visible=0, size=(1024, 768))
	display.start()


	# create a browser using Splinter library and simulate the workflow of a user logging in
	# various time.sleep(n) is inserted here to make sure login is successful even on slower connections > replaced with HumanCondition.HumanCondition(5,8)
	with Browser() as browser:
		# Visit URL
		url = redirect_response
		browser.visit(url)
		
		if browser.is_element_present_by_name('txtPassword', wait_time=0):
			
			browser.fill('USER', OAuth1Credentials.username)
			HumanCondition.HumanCondition(5,8)


			browser.find_by_name('txtPassword').click()
			
			HumanCondition.HumanCondition(5,8)
			# pprint(browser.html)

			browser.fill('PASSWORD', OAuth1Credentials.userpass)
			# Find and click the 'logon' button
			browser.find_by_name('Logon').click()
			HumanCondition.HumanCondition(5,8)
			if browser.is_element_present_by_name('continueButton', wait_time=2):
				browser.find_by_name('continueButton').click()

			browser.find_by_value('Accept').click()
			HumanCondition.HumanCondition(5,8)
			# authCode = browser.find_by_xpath("//@type='text'").first.value
			authCode = browser.find_by_tag("input").first.value
			HumanCondition.HumanCondition(5,8)

	display.stop()
	
	return authCode
	
def authorizeToken_manual(requestTokenResponse):
	'''
		Manual eTrade Login
		1) Generate url to follow
		2) Open up browser
		3) Manually login and copy over verification code
	'''

	resource_owner_key = requestTokenResponse['oauth_token']
	resource_owner_secret = requestTokenResponse['oauth_token_secret']
	redirect_response = 'https://us.etrade.com/e/t/etws/authorize?key={}&token={}'.format(client_Consumer_Key,resource_owner_key)
	
	#display.start() THIS IS FOR LINUX, FOR WINDOWS I'm SWITCHING OVER TO "webbrowser"

	# Edit below_ John Freeman: for windows systems
	# Visit URL
	print'Goto following URL for manual login:'
	print redirect_response

	url = redirect_response
	webbrowser.open(url)
	authCode = raw_input('Enter Verification Code: ')
	
	return authCode


# return redirect_response
def accessToken(requestTokenResponse, verifier = None):
	"""
	Using the authCode <str> generated by authorizeToken(), we pass this as verifier <str> 
	and the function returns a dict containing the persistent oauth token and secret
	"""
	if verifier is None:
		verifier = raw_input('Paste the login verifier code here: ')

	access_token_url = 'https://etws.etrade.com/oauth/access_token'
	oauth = OAuth1Session(	client_key = client_Consumer_Key,
							client_secret=client_Consumer_Secret,
							resource_owner_key=requestTokenResponse['oauth_token'],
							resource_owner_secret=requestTokenResponse['oauth_token_secret'],
							verifier=verifier)

	oauth_tokens = oauth.fetch_access_token(access_token_url)
	user_access_token = oauth_tokens.get('oauth_token')
	user_access_token_secret = oauth_tokens.get('oauth_token_secret')
	# print oauth_tokens
	return oauth_tokens

def renewAccessToken():
	"""
	When the persistent token and secret is expired, the tokens will need to be renewed.
	The function returns a dict containing the renewed persistent oauth token and secret
	
	* generally speaking this doesn't normally work :/
	"""
	url = 'https://etws.etrade.com/oauth/renew_access_token'

	oauth = OAuth1(	client_key				= OAuth1Credentials.client_Consumer_Key,
					client_secret			= OAuth1Credentials.client_Consumer_Secret,
					resource_owner_key		= OAuth1Credentials.client_Token,
					resource_owner_secret	= OAuth1Credentials.client_Token_Secret
			)

	r = requests.post(url=url, auth=oauth)

	# print r.content
	return r.content

def login():
	"""
	Tries to inititate the login process and creates a token for the user
	"""
	# A) Load previous token session
	if OAuth1Credentials.load_session():
		# Try to access an OAuth page(can still generate error if token dead)
		testState = listAccounts(requestRawData=True)
	else:
		# Previous session not found, set teststate to error, to force login
		testState = {'Error':'Login'}

	# try renewing access token first,
	if 'Error' in testState:
		print 'trying to renew token...'

		oauth_tokens = renewAccessToken()
		testState = listAccounts()

	# if it doesn't work then try manual login process
	if 'Error' in testState:
		# if testState == {u'Error': {u'message': u'oauth_problem=token_expired'}} or testState == {u'Error': {u'message': u'oauth_problem=token_rejected'}} or testState == {u'Error': {u'message': u'Invalid access token used'}}:
		print 'trying to manually login... '
		r = getRequestToken()
		authCode = authorizeToken(r)
		oauth_tokens = accessToken(r, verifier = authCode)
		
	# B) Collect tokens and save
	try:
		OAuth1Credentials.client_Token = oauth_tokens.get('oauth_token')
		OAuth1Credentials.client_Token_Secret = oauth_tokens.get('oauth_token_secret')
		OAuth1Credentials.save_session()
	except:
		pass
	
	# j.freeman
	global Logged_IN
	Logged_IN = True
	
	print'Logged into eTrade'

def accessMethod(url, method = 'GET', payload = None, requestRawData=False, *args, **kwargs):
	"""
	This is a generic function that calls for url <str> and method <'GET' or 'POST'>. If using 'POST', a payload <dict> should be supplied
	function returns a dict containing the output of the url called.
	
	requestRawData specifies if data returned should be string for dict
		True = dict returned
		False = string returned
	"""

	oauth = OAuth1(	client_key				= OAuth1Credentials.client_Consumer_Key,
					client_secret			= OAuth1Credentials.client_Consumer_Secret,
					resource_owner_key		= OAuth1Credentials.client_Token,
					resource_owner_secret	= OAuth1Credentials.client_Token_Secret
			)

	try:
		if method == 'GET':
			r = requests.get(url = url, auth=oauth)
		
		elif method == 'POST':
			headers = {'Content-Type': 'application/json'}
			# r = requests.post(url = url, auth=oauth, data = json.dumps(payload), headers = headers)
			r = requests.post(url = url, auth=oauth, data = json.dumps(payload), headers = headers)
	
		else:
			raise "Invalid method: {}, please use only 'GET' or 'POST'".format()
			
			
		# HANDLING THE RESULT
		response = r.content
	
	except:
		# Something happened during request
		print'eTrade low-level request error detected'
		response = '{"Error":"eTrade low-level request error"}'
	
	if Debug:
		# Content is string object
		print response #j.freeman test
	
	# Check for errors from server and respond
	'''
		1) quick check for the word error in string without parsing
		2) if 'error' word found, continue to parse and do final check for error state
	'''
	
	# Run Checks if logged in and program running, response handled differently when not logged in
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
		eTrade has a few hick-ups that need to be dealt with
	'''
	_dict = json_handle.parse_json2dict(input)
	
	if not 'Error' in _dict:
		# Clean _dict
		return input
	
	else:
		print '\nError in Response:', input
		Error = _dict['Error']
	
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
	
	# As of new method, return string, this will later be converted if need be
	return "{'Error':'Other'}"

		
# Accounts

def listAccounts( *args, **kwargs):
	"""
	Lists all the accounts of the user. 
	For more info see etrade's documentation
	"""
	url = urlRoot().format('accounts','accountlist')
	return accessMethod(url, *args, **kwargs)

def getAccountBalance(AcctNumber, *args, **kwargs):
	"""
	Lists all the balance info on an account given an AcctNumber <str>. 
	For more info see etrade's documentation
	"""
	url = urlRoot().format('accounts','accountbalance/{}'.format(str(AcctNumber)))
	return accessMethod(url, *args, **kwargs)

def getAccountPositions(AcctNumber, *args, **kwargs):
	"""
	Lists all the positions in an account given an AcctNumber <str>. 
	For more info see etrade's documentation
	"""
	url = urlRoot().format('accounts','accountpositions/{}'.format(str(AcctNumber)))
	return accessMethod(url, *args, **kwargs)

def getTransactionHistory(AcctNumber, *args, **kwargs):
	"""
	Lists all the transaction history in an account given an AcctNumber <str>. 
	For more info see etrade's documentation
	"""
	url = urlRoot().format('accounts',(AcctNumber+'/transactions'))
	return accessMethod(url, *args, **kwargs)

def getTransactionDetails(detailsURL, *args, **kwargs):
	"""
	Lists details on a specific trade given a URL
	For more info see etrade's documentation
	"""
	return accessMethod(detailsURL+'.json', *args, **kwargs)


def getOptionChains(
					chainType,
					expirationDay,
					expirationMonth, 
					expirationYear, 
					underlier, 
					skipAdjusted = True, 
					*args,
					**kwargs):
	"""
	Gets Option Chain information according to an underlier <str> stock/company
	sample usage:
	pprint (getOptionChains(	expirationMonth=04,
								expirationYear=2015,
								chainType='PUT',
								skipAdjusted=True,
								underlier='GOOG'))
	**attempting to quess expirationDay ** j.freeman @ it worked on the first try! Day-month-year
	"""

	if skipAdjusted:
		skipAdjusted = 'true'
	else:
		skipAdjusted = 'false'

	url = urlRoot().format('market','optionchains') + '?' + \
		'chainType={}&'.format(chainType) + \
		'expirationDay={}&'.format(expirationDay) + \
		'expirationMonth={}&'.format(expirationMonth) + \
		'expirationYear={}&'.format(expirationYear) + \
		'underlier={}&'.format(underlier) + \
		'skipAdjusted={}'.format(skipAdjusted)

	return accessMethod(url, *args, **kwargs)

def getOptionExpireDate(underlier, *args, **kwargs):
	"""
	Returns the expiration date of the most recent option chain for the underlier <str>

	sample usage:
	getOptionExpireDate('GOOG'))
	"""
	url = urlRoot().format('market','optionexpiredate') + '?' + \
	 'underlier={}'.format(underlier)
	return accessMethod(url, *args, **kwargs)

def lookupProduct(company, assetType ='EQ', *args, **kwargs):
	"""
	assetType <str> can only by EQ for Equity or MF for mutual fund
	company <str> is the ticker of the company

	sample usage:
	lookupProduct('GOOG')

	"""
	# 
	url = urlRoot().format('market','productlookup') + '?' + \
	 'company={}&'.format(company) + \
	 'type={}'.format(assetType)
	print url
	return accessMethod(url, *args, **kwargs)

def getQuote(symbolStringCSV, detailFlag = 'ALL' , *args, **kwargs):
	"""
	Returns the live quote of a single or many companies
	symbolStringCSV <str> is a comma separated value of tickers
	detailFlag <'ALL' or 'INTRADAY'> specifies whether all data is returned or just a subset with intraday

	sample usage:
	getQuote('TVIX, GOOG', detailFlag = 'INTRADAY')

	"""
	url = urlRoot().format('market','quote/'+symbolStringCSV) + '?' + \
	 'detailFlag={}'.format(detailFlag)
	# print url
	return accessMethod(url, *args, **kwargs)

# Order API

def listOrders(AcctNumber, marker = None, *args, **kwargs):
	"""
	Lists all orders made during the day for an accounts given AcctNumber <str>
	marker <str> retreives different pages of orders if the number of orders exceed a certain number.
	For more information on limits, see etrade's documentation

	sample usage:
	pprint(listOrders('35832156'))
	"""
	
	# rather complex, need to parse for useful parts of all orders of the day
	url = urlRoot().format('order','orderlist/{}'.format(AcctNumber))+ '?' + \
	 'count={}'.format(25)

	if not(marker is None):
		# if marker is not none then extend the url to include param
		url += '&marker={}'.format(marker)


	# check for marker if it is absent or empty '', then there are no more pages left, API is restrained to return 25 orders max at a time
	resp = accessMethod(url, *args, **kwargs)
	# print resp

	try:
		numOfOrders = resp['GetOrderListResponse']['orderListResponse']['count']
	except:
		numOfOrders = 0

	# print 'number of orders: ', resp['GetOrderListResponse']['orderListResponse']['count']

	if numOfOrders == 0:
		return None
	elif 'marker' in resp['GetOrderListResponse']['orderListResponse']:
		print 'there are more orders'
		marker = resp['GetOrderListResponse']['orderListResponse']['marker']
		resp = resp + listOrders(AcctNumber, marker )
		return resp
	else:
		return resp['GetOrderListResponse']['orderListResponse']['orderDetails']

def previewEquityOrder(
						AcctNumber,
						symbol,
						orderAction,
						quantity,
						priceType, 
						clientOrderId = None,
						limitPrice = None, 
						stopPrice = None,
						allOrNone = False, 
						reserveOrder = False, 
						reserveQuantity = None, 
						marketSession = 'REGULAR',
						orderTerm = 'GOOD_FOR_DAY',
						routingDestination = 'AUTO',
						sendPost=True,		# Note(A) j.freeman, used to enable grab params directly below
						*args,
						**kwargs):

	"""
	Used to stage an order to specify all the order details before actually sending the trade.
	Returns liveParams <dict> required to place the trade and also resp <dict> which are responses from the API regarding the staged trade.
	For example resp might tell you if the trade is staged correctly and free of syntax errors

	For more information, see etrade's documentation
	"""

	# generate a 20 alphanum random client order ID, needed later for actual order generation:
	if clientOrderId is None:
		clientOrderId = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))

	EquityOrderRequest = {
			 "accountId": AcctNumber,

			 "symbol": symbol,
			 "orderAction": orderAction,
			 "clientOrderId": clientOrderId,
			 "priceType": priceType, 
			 "quantity": quantity,

			 "marketSession": marketSession,
			 "orderTerm": orderTerm,
			 "routingDestination": routingDestination
			 
		 }

	# special cases for conditional inputs
	if priceType == 'STOP':
		EquityOrderRequest['stopPrice'] = stopPrice
	elif priceType == 'LIMIT':
		EquityOrderRequest['limitPrice'] = limitPrice
	elif priceType == 'STOP_LIMIT':
		EquityOrderRequest['stopPrice'] = stopPrice
		EquityOrderRequest['limitPrice'] = limitPrice

	if reserveOrder == True:
		EquityOrderRequest['reserveOrder'] = 'TRUE'
		EquityOrderRequest['reserveQuantity'] = reserveQuantity


	params = {
	 "PreviewEquityOrder": {
		"-xmlns": "http://order.etws.etrade.com",
		'EquityOrderRequest' : EquityOrderRequest
		}
	}
	'''
	# sample params used for testing
	params = {
	 "PreviewEquityOrder": {
			"-xmlns": "http://order.etws.etrade.com",
			"EquityOrderRequest": {
				"accountId": "83405188",
				"stopPrice": "197",
				"quantity": "4",
				"symbol": "IBM",
				"orderAction": "BUY",
				"priceType": "STOP",
				"marketSession": "REGULAR",
				"orderTerm": "GOOD_FOR_DAY",
				"clientOrderId": "random123456"
			}
		}
	}
	'''

	# These are the params needed for placing actual order
	liveParams = {
	 "PlaceEquityOrder": {
		"-xmlns": "http://order.etws.etrade.com",
		'EquityOrderRequest' : EquityOrderRequest
		}
	 }


	# Note(A) if not to be sent, returns params only
	if sendPost:
		url = urlRoot().format('order','previewequityorder')
		resp = accessMethod(url = url, method = 'POST', payload = params, *args, **kwargs)
	
		return liveParams, resp
	
	else:
		return liveParams
	
def placeEquityOrder(liveParams, *args, **kwargs):
	"""
	liveParams <dict> an dict output generated by previewEquityOrder()
	function actually places the order that was previously staged via previewEquityOrder(), returns a dict that indicates status of trade

	"""
	# liveParams should be generated through previewEquityOrder
	url = urlRoot().format('order','placeequityorder')
	resp = accessMethod(url = url, method = 'POST', payload = liveParams, *args, **kwargs)
	return resp

def previewEquityOrderChange(AcctNumber, orderNum, quantity, priceType, 
												clientOrderId = None,
												limitPrice = None, 
												stopPrice = None,
												allOrNone = False, 
												reserveOrder = False, 
												reserveQuantity = None, 
												orderTerm = 'GOOD_FOR_DAY',
												*args,
												**kwargs
											):

	"""
	For an active order, the order params may be changed. 
	clientOrderId <str> is supplied by the API on the original trade.

	Returns liveParams <dict> required to place the changes trade and also resp <dict> which are responses from the API regarding the staged trade.
	For example resp might tell you if the trade is staged correctly and free of syntax errors.

	For more information, see etrade's documentation
	"""
	# generate a 20 alphanum random client order ID, needed later for actual order generation:
	if clientOrderId is None:
		clientOrderId = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))

	changeEquityOrderRequest = {
			 "accountId": AcctNumber,
			 "orderNum": orderNum,

			 "clientOrderId": clientOrderId,
			 "priceType": priceType, 
			 "quantity": quantity,

			 "orderTerm": orderTerm,
			 
		 }

	# special cases for conditional inputs
	if priceType == 'STOP':
		changeEquityOrderRequest['stopPrice'] = stopPrice
	elif priceType == 'LIMIT':
		changeEquityOrderRequest['limitPrice'] = limitPrice
	elif priceType == 'STOP_LIMIT':
		changeEquityOrderRequest['stopPrice'] = stopPrice
		changeEquityOrderRequest['limitPrice'] = limitPrice

	if reserveOrder == True:
		changeEquityOrderRequest['reserveOrder'] = 'TRUE'
		changeEquityOrderRequest['reserveQuantity'] = reserveQuantity

	if allOrNone == False:
		changeEquityOrderRequest['allOrNone'] = 'FALSE'
	else:
		changeEquityOrderRequest['allOrNone'] = 'TRUE'

	params = {
	 "previewChangeEquityOrder": {
		"-xmlns": "http://order.etws.etrade.com",
		'changeEquityOrderRequest' : changeEquityOrderRequest
		}
	 }

	liveParams = {
	 "placeChangeEquityOrder": {
		"-xmlns": "http://order.etws.etrade.com",
		'changeEquityOrderRequest' : changeEquityOrderRequest
		}
	 }

	url = urlRoot().format('order','previewchangeequityorder')
	resp = accessMethod(url = url, method = 'POST', payload = params, *args, **kwargs)
	return liveParams, resp

def placeEquityOrderChange(liveParams, *args, **kwargs):
	"""
	liveParams <dict> an dict output generated by previewEquityOrderChange()
	function actually places the order change that was previously staged via previewEquityOrderChange(), 
	returns a dict that indicates status of trade

	"""
	# liveParams should be generated through previewEquityOrderChange
	url = urlRoot().format('order','placechangeequityorder')
	resp = accessMethod(url = url, method = 'POST', payload = liveParams, *args, **kwargs)
	return resp

def cancelOrder(AcctNumber, orderNum, *args, **kwargs):
	"""
	Cancels an active order given an AcctNumber <str> and orderNum <int>.
	The orderNum can be found when the trade is first placed via the output of placeEquityOrder() 
	Returns a dict to indicate whether cancelOrder is successful
	"""

	url = urlRoot().format('order','cancelorder')
	params = {
	 "cancelOrder": {
		 "-xmlns": "http://order.etws.etrade.com",
		 "cancelOrderRequest": {
			 "accountId": AcctNumber,
			 "orderNum": orderNum
			}
		}
	}
	resp = accessMethod(url = url, method = 'POST', payload = params, *args, **kwargs)
	return resp

# Limits API

def getLimits(*args, **kwargs):
	"""
	Returns the limits of the API
	"""
	url = urlRoot().format('statuses','limits')
	return accessMethod(url, *args, **kwargs)

# Notifications API

def getNotifications(*args, **kwargs):
	"""
	Returns messages for developers
	"""
	# gets message for developers only, doesn't seem to work on sandbox.
	url = urlRoot().format('notification','getmessagelist')
	return accessMethod(url, *args, **kwargs)

# ****************START**J.FREEMAN***********************************
'''
	Currently missing the ability to place options orders.
	My functions will also 
'''
def previewOptionOrder( AcctNumber = None,
						SymbolInfoList = [None,None,None,None,None,None],
						orderAction = None,
						quantity = None,
						priceType = None, 
						limitPrice = None, 
						stopPrice = None,
						allOrNone = False, 
						reserveOrder = False, 
						reserveQuantity = None, 
						marketSession = 'REGULAR',
						orderTerm = 'GOOD_FOR_DAY',
						routingDestination = 'AUTO',
						clientOrderId = None,
						sendPost = True,	# See note below
						*args,
						**kwargs):

	"""
		Modifying Hualan's Equity preview code, adding in one more variable sendPost = True,
	when False, this function only returns the live params instead of executing the sendPost, saving 0.25 seconds in trade execution.
	"""

	# generate a 20 alphanum random client order ID, needed later for actual order generation:
	if clientOrderId is None:
		clientOrderId = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))

	symbolInfo = {
			"symbol": SymbolInfoList[0],
			"callOrPut": SymbolInfoList[1],
			"strikePrice": SymbolInfoList[2],
			"expirationYear": SymbolInfoList[3],
			"expirationMonth": SymbolInfoList[4],
			"expirationDay": SymbolInfoList[5]
	}
	OptionOrderRequest = {
			"accountId"		: AcctNumber,
			"clientOrderId"	: clientOrderId,
		 
			"quantity"		: quantity,
			"symbolInfo"	: symbolInfo,
			"orderAction"	: orderAction,
			"priceType"		: priceType,	 
			"orderTerm"		: orderTerm,
			"routingDestination": routingDestination
		 }

	# special cases for conditional inputs
	if priceType == 'STOP':
		OptionOrderRequest['stopPrice'] = stopPrice
	elif priceType == 'LIMIT':
		OptionOrderRequest['limitPrice'] = limitPrice
		if limitPrice == None:
			print('priceType "LIMIT" requires corresponding limitPrice **kwargs')

	elif priceType == 'STOP_LIMIT':
		OptionOrderRequest['stopPrice'] = stopPrice
		OptionOrderRequest['limitPrice'] = limitPrice

	if reserveOrder == True:
		OptionOrderRequest['reserveOrder'] = 'TRUE'
		OptionOrderRequest['reserveQuantity'] = reserveQuantity


	params = {
	 "PreviewOptionOrder": {
		"-xmlns": "http://order.etws.etrade.com",
		'OptionOrderRequest' : OptionOrderRequest
		}
	 }

	'''
	# sample params used for testing
	params = {
		"PreviewOptionOrder": {
			"-xmlns": "http://order.etws.etrade.com",
			"OptionOrderRequest": {
				"accountId": "83405188",
				"quantity": "1",
				"symbolInfo": {
					"symbol": "IBM",
					"callOrPut": "CALL",
					"strikePrice": "115",
					"expirationYear": "2010",
					"expirationMonth": "4",
					"expirationDay": "17"
				},
				"orderAction": "BUY_OPEN",
		"priceType": "MARKET",
		"orderTerm": "GOOD_FOR_DAY"
			}
		}
	}
	'''

	# These are the params needed for placing actual order
	liveParams = {
		"PlaceOptionOrder": {
			"-xmlns": "http://order.etws.etrade.com",
			'OptionOrderRequest' : OptionOrderRequest
		}
	}

	if sendPost:
		url = urlRoot().format('order','previewoptionorder')
		resp = accessMethod(url = url, method = 'POST', payload = params, *args, **kwargs)
	
		return liveParams, resp

	else:
		return liveParams


def placeOptionOrder(liveParams, *args, **kwargs):
	"""
	liveParams <dict> an dict output generated by previewoptionorder()
	function actually places the order that was previously staged via previewoptionorder(), returns a dict that indicates status of trade
	"""
 
	# liveParams should be generated through previewoptionorder
	url = urlRoot().format('order','placeoptionorder')
	return accessMethod(url = url, method = 'POST', payload = liveParams, *args, **kwargs)

# ****************END****J.FREEMAN***********************************


if __name__ == "__main__":
	login()
	# print listAccounts()
	pass
	# etst

