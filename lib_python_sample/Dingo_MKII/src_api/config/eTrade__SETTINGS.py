'''
client_Consumer_Key= "828540e231a0c6416c4c095741c2928c"
client_Consumer_Secret= "removed"

username = "removed"
userpass = "removed"
'''

'''
sandboxMode = True

client_Consumer_Key= "6d7851225a7d9ddedd422f7ff7976145"
client_Consumer_Secret= "removed"

username = "removed"
userpass = "removed"

'''
CONFIG_ETRADE = {
	'sandboxMode'				: False,
	
	'client_Consumer_Key'		: "db1ae8b54eb51ea6dea72614a6a8cc4e",
	'client_Consumer_Secret'	: "removed",
	
	'username'					: "removed",
	'userpass'					: "removed",
	
	'token_filename'			: "eTrade_user_tokens.p",
}

CONFIG_API = {
	'num_BatchSymbols'		: 25,	# Emperical test, due to limited consumer router speed
	'minDelay'				: 0.25,	# User defined, since 4 per second, we just use 0.25 as self imposed minimum
	'request_timeout'		: 2,
	'processDelay'			: 0.02, # Maximum Seconds API process should wait in between process cycles, ie, get a command, the delay between loops
	
	# Track API Rates
	'heartbeat'				: 1,	# seconds till refresh
	'allowance_Public'		: 4,	# number per heartbeat
	'allowance_Private'		: 2,
	
	'N_WeeklyExpirationDates'	: 2,
}