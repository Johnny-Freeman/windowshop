import urllib2
from utils import json_handle
from config.IEX__SETTINGS import CONFIG_API

Debug=False

def READ_GET_IEXreponse(url_request, requestRawData=False, *args, **kwargs):
	'''
		Acts as simple HTTP socket, possible future versions will include params={} and headers if api calls for it
			for now, API seems simple enough to not need it
	'''
	# Attempt to retrieve a response
	try:
		response = urllib2.urlopen(urllib2.Request(url_request))
		pagereturn = response.read()
	
	except:
		str_warning = 'Warning: Issue with grabbing ' + url_request[:42] + '...) information'
		print( str_warning )
		pagereturn='{"Error":"' + str_warning +  '"}'
		
	if Debug:
		print pagereturn
		
		# Check for errors from server and respond
	'''
		1) quick check for the word error in string without parsing
		2) if 'error' word found, continue to parse and do final check for error state
	'''
	
	# 1) Quick Error Check
	if json_handle.CHECK_quickError(pagereturn):
	
		# 2) parse and do in-depth error check		
		pagereturn = ChecknHandle_ServerErrors(pagereturn)
		
	if requestRawData:
		return pagereturn
	else:
		return json_handle.parse_json2dict(pagereturn)

def ChecknHandle_ServerErrors(input):
	'''
		input is string response object > convert to _dict_ first
		eTrade has a few hick-ups that need to be dealt with
	'''
	_dict = json_handle.parse_json2dict(input)
	
	if (not 'error' in _dict) and  (not 'Error' in _dict):
		# Clean _dict
		return input
	
	else:
		print '\nError in Response:', input
		try:
			Error = _dict['error']
		except:
			pass
		
		try:
			Error = _dict['Error']
		except:
			pass
	
	# As of new method, return string, this will later be converted if need be
	return "{'Error':'" + str(Error) + "'}"

# *****GET MARKET DATA**********************************************
	
def GET_singleQuote(tick, *args, **kwargs):
	#make request string
	reqstring = "https://api.iextrading.com/1.0/stock/" + tick + "/quote"

	return READ_GET_IEXreponse(reqstring, *args, **kwargs)

def GET_singleChart(tick, *args, **kwargs):
	reqstring = "https://api.iextrading.com/1.0/stock/" + tick + "/batch?types=chart&range=1d"
	
	return READ_GET_IEXreponse(reqstring, *args, **kwargs)

def GET_singleQuoteChart(tick, *args, **kwargs):
	reqstring = "https://api.iextrading.com/1.0/stock/" + tick + "/batch?types=quote,chart&range=1d"
	
	return READ_GET_IEXreponse(reqstring, *args, **kwargs)
	
def GET_100batch(batch, types, *args, **kwargs):
	'''
		Return 100batch(array) of quotes from IEX
		Maximum quote limit is 100
	'''

	if len(batch) > CONFIG_API['num_BatchSymbols']:
		raise ValueError('IEXs 100batch wrapper only takes 100 symbols at a time')
		return False

	# Make batch string
	reqstring = "https://api.iextrading.com/1.0/stock/market/batch?symbols="
	for i in range(0,len(batch)):
		reqstring += batch[i] + ","
	
	#remove last ,char
	reqstring = reqstring[:-1]
	
	#add types
	reqstring += "&types=" + types
	
	'''Only a few ways of grabbing data, no biggie to move to static types
	for i in range(0,len(types)):
		reqstring += types[i] + ","
	
	#remove last ,char
	reqstring = reqstring[:-1]
	'''
	
	return READ_GET_IEXreponse(reqstring, *args, **kwargs)