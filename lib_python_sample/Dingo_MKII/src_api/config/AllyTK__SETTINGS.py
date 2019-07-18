'''
	Ally (Trade King) settings
'''

CONFIG_API = {
	'num_BatchSymbols'		: 26,	# Emperical test, due to limited consumer router speed, even though 256 allowed, this allows recovery if a few don't make it( also 52 stock requests + 26 option requests at a time(x2 batches x4a mint = 8 more requests), totalling 60 a minute)
	'minDelay'				: 0.13,	# Even though unlimited speed allowed, realistically I need to impose my own limits due to some of the regexp functions which check the data for dl errors, and bandwidth issues
	'request_timeout'		: 8.8,	# 6.32 + 4x stdev(0.62) request time
	'processDelay'			: 0.02, # Maximum Seconds API process should wait in between process cycles, ie, get a command, the delay between loops
	
	# Track API Rates
	'heartbeat'				: 60,	# seconds till refresh
	'allowance_Public'		: 60,	# number per heartbeat
	'allowance_Private'		: 20,
	
	# Syncronize Data requests
	# '''
	# 	Here we try to define times to relative to the START OF A MINUTE to grab data
	# 		, specified as a list of seconds since the start of the first second of the sync'd minute
	# 		, last bit is a range to generate a random wait period from the start of the sync list
	# 			if you want to make a request at 3 seconds with a random period of (-1,1) seconds, do sync_list = [2] sync_noiseRequest = [0,2] < its +-1 centered at 3
	# '''
	'sync_stock_1minChart'	: [7],				# [7] subtract the noise center
	'sync_option_tables'	: [0,14,29,44],		# [1,15,30,45] subtract the noise center
	'sync_noiseRequest'		: [0,0],			# Centered at +1, +-1, somehow this adds in a parasitic effect! so weird
	
	# Data Fields (Primarily around options)
	'fids'					: ['ask','asksz','bid','bidsz','cl','date','exch','hi','idelta','igamma','imp_Volatility','incr_vl','irho','itheta','ivega','last','lo','op_style','openinterest','opn','put_call','pvol','rootsymbol','strikeprice','symbol','tcond','timestamp','tr_num','undersymbol','vl','vwap','xdate','xday','xmonth','xyear'],
	#recommended fids		: ['ask','asksz','bid','bidsz','cl','date','exch','hi','idelta','igamma','imp_Volatility','incr_vl','irho','itheta','ivega','last','lo','op_style','openinterest','opn','put_call','pvol','rootsymbol','strikeprice','symbol','tcond','timestamp','tr_num','undersymbol','vl','vwap','xdate','xday','xmonth','xyear'],
	
	'N_WeeklyExpirationDates'	: 2,
}


# ******Settings*************************************
token_filename = 'AllyTK_user_tokens.p'


# Static Oauth (single user token)***********************
CONFIG_UR1 = {	'sandboxMode'			: False,
				'username'				: 'removed',
				'userpass'				: 'removed',
				'client_Consumer_Key'	: 'HLqH8u4E5X9Q12N5VOe8e9tKoN6zPb1ETLDaVMJerror', #'HLqH8u4E5X9Q12N5VOe8e9tKoN6zPb1ETLDaVMJx0tc2',
				'client_Consumer_Secret': 'removed', #'removed',
				'client_Token'			: 'jh5O80smh44NQqbP3MxXZ36EceeyRdPs2sDK7heerror', #'jh5O80smh44NQqbP3MxXZ36EceeyRdPs2sDK7heD2bc0', #optional, for static tokens
				'client_Token_Secret'	: 'removed',#'removed', #optional
				'token_filename'		: token_filename,
}                       
                                            
CONFIG_UR2 = {	'sandboxMode'			: False,
				'username'				: 'removed',
				'userpass'				: 'removed',
				'client_Consumer_Key'	: 'FFkTdt5Yxv1qoi9b9LGuKCG0SaJoKWkyoza8UrmRueQ8',
				'client_Consumer_Secret': 'removed',
				'client_Token'			: '4o49P1NZCTPoHPx8EMopZbtEuV1jq81dCp7oi5JGRtE1', #optional, for static tokens
				'client_Token_Secret'	: 'removed', #optional
				'token_filename'		: token_filename,
}

CONFIG_UR3 = {	'sandboxMode'			: False,
				'username'				: 'removed',
				'userpass'				: 'removed',
				'client_Consumer_Key'	: 'tHi3ZioOaSVl883M39wjh5Rq6VVYh0KY04dtycviO7g1',
				'client_Consumer_Secret': 'removed',
				'client_Token'			: '2802gGRQMLvtyq5cR3X7vnpQEetawzb7s3sKKqlHk0k8', #optional, for static tokens
				'client_Token_Secret'	: 'removed', #optional
				'token_filename'		: token_filename,
}