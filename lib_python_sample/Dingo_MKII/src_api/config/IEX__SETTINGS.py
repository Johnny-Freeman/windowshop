'''
	IEX Configuration Settings
'''

CONFIG_API = {
	'num_BatchSymbols'		: 100,
	'minDelay'				: 1.3,	# User defined, since 100 per second
	'request_timeout'		: 7,	# Data requests can be large
	'processDelay'			: 0.1,	# Maximum Seconds API process should wait in between process cycles, ie, get a command, the delay between loops
	
	# Track API Rates
	'heartbeat'				: 1,	# seconds till refresh
	'allowance_Public'		: 100,	# number per heartbeat
	'allowance_Private'		: 2,
	
	# DataGrab times and offsets
	'offset_1minchart'		: 17,	# IEX has a slow internal server update!
}