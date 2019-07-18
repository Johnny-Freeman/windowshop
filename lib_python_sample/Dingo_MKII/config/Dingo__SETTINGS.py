'''
	Holds all settings for Dingo Data Scavenger (DDS)
'''
# **************************************************************************************
'''
	Combine Lists
	# Stocks_of_interest = combine_lists(Stocks_of_interest,Super_Screened)
	# EOD_Options_of_interest = combine_lists(Options_of_interest, Super_Screened)
'''
def combine_lists(first_list,second_list):
	resulting_list = list(first_list)
	resulting_list.extend(x for x in second_list if x not in resulting_list)
	return resulting_list
# **************************************************************************************

'''
	Stocks_of_interest = list of all stocks to grab data for on a CONTINUOUS basis from IEX, for both candle AND individual quote information
		IEX's 1min charts update the PREVIOUS minute, but provides zero information about the current minute.
		Here additional stock info will also be gathered through out a minute to supplement the 1 minute candles.
		+ 1 minute candles, readings lag by 1 minute, this grabs BOTH chart and quote in one go
		+ Stock1min_fidelity = N, represents the N-1 mid-minute stock readings to be made (Samples per minute)
	
'''
# Limited by AllyTK limits
Options_of_interest = ['AAPL','FB','BABA','MSFT','NVDA','NFLX','JPM','WMT','AMZN','TSLA','IBM','BA','UPS','UNP','ABBV','CAT','DIS','EA','V','CVX','HD','JNJ','CELG','GS','JNUG','MCD','WYNN','BIDU','AGN','SWKS','LOW','CRM','GOOGL','UTX','FDX','WDC','GLD','ADBE','AMGN','MMM','AXP','HAS','MAR','AVGO','PEP','VLO','VMW','MA','KMB','STZ','COST'] 

# Limited by eTrade limits (options of interest + ranked mid_sized weeklys)
Stocks_100_interest = ['AAPL','FB','BABA','MSFT','NVDA','NFLX','JPM','WMT','AMZN','TSLA','IBM','BA','UPS','UNP','ABBV','CAT','DIS','EA','V','CVX','HD','JNJ','CELG','GS','JNUG','MCD','WYNN','BIDU','AGN','SWKS','LOW','CRM','GOOGL','UTX','FDX','WDC','GLD','ADBE','AMGN','MMM','AXP','HAS','MAR','AVGO','PEP','VLO','VMW','MA','KMB','STZ','COST','BAC','MU','GE','PBR','AMD','KR','VALE','TWTR','SNAP','C','F','CSCO','FCX','VRX','INTC','AMAT','MGM','SQ','M','CMCSA','ABX','TEVA','EBAY','ORCL','JD','WFC','XOM','DAL','X','GM','T','PFE','MS','KMI','ROKU','VZ','UAA','MDT','GILD','QCOM','SBUX','BBY','KO','TGT','CVS','PG','ATVI','BMY']

# EOD lists to Grab
FinvizMidSized = ['X','ETSY','ROKU','STLD','NUE','BRX','WEN','SLCA','KIM','RPAI','OHI','SNAP','MT','ABBV','CAR','AMT','MPW','SABR','ORI','AR','IVZ','TRIP','NWL','EMR','CVS','AMAT','OMC','ABC','CAH','HCP','HRB','CNHI','PEG','HSIC','SU','HST','WBA','MU','TAL','FNB','EIX','PBF','EXPE','XL','DE','NKTR','ZTS','ESRX','PFE','WMT','BHGE','UNH','VTR','JNJ','SLM','AEO','CPE','AFL','O','CCI','NOV','FOXA','NXPI','GE','WM','HAL','DIS','BLL','DFS','LLY','VLY','LRCX','MYL','AMH','ABT','PPL','VRX','HCN','MCHP','XEL','PCG','PAH','IPG','UNIT','SYY','CMS','GSK','DHI','PGR','NYCB','CSX','DRE','PLD','USB','HD','MAS','SM','COF','AEP','GPK','ED','VZ','NFX','PHM','ADI','VOD','HRL','QD','CTRP','TWO','EBAY','MMM','LEN','AET','EXC','STI','FE','AGNC','KSS','MOMO','WY','DUK','MTG','TV','JCI','PM','CPN','IP','CSCO','CNP','ARNC','ALL','MA','ZION','QVCA','MRK','BCS','WP','PAYX','PBCT','D','NI','KO','MDT','WDC','XOM','TEVA','TSLA','ITUB','BSX','AIG','HON','MMC','CZR','T','NLY','NUAN','CL','KEY','YNDX','WU','VLO','UNP','HOLX','HES','CIEN','HPE','KMB','AXP','NLSN','BBT','PG','MO','CS','COP','MPC','CNDT','PE','WYNN','XRX','BK','LUV','CHD','DWDP','ORCL','MDLZ','FLEX','HAWK','IBM','SLB','EQR','BEN','CSRA','PYPL','MXIM','PEP','SC','FHN','ETN','APA','IVV','NKE','JBLU','FCAU','DISH','RGC','GS','AMGN','BMY','EOG','A','VALE','DKS','TSM','TXN','INFY','WFC','TJX','FL','CC','CCL','RF','NRG','ADM','BAX','AAL','SBUX','GPS','DB','DAL','HBAN','BBY','MET','STX','CFG','ABB','FTI','CNX','LOW','FITB','K','CRM','HPQ','GLW','SWKS','AGN','MRVL','AZN','PRU','USFD','CERN','PCAR','SYF','CAG','SCHW','AAPL','UAL','VIPS','C','DPS','NBL','TER','CVX','KR','V','GGP','EA','COTY','BA','BX','SQ','JUNO','NRZ','BBD','AA','TGT','MS','PNC','BB','CTSH','SEE','SYMC','ROST','PBR','BP','DLTR','UTX','HIG','NYT','MFC','NFLX','TMUS','QCOM','COG','AES','NWSA','ADBE','ING','SKX','PAA','MSFT','JPM','ECA','CMCSA','APC','BAC','DISCA','M','NEM','INTC','GIS','ENB','CLR','WPX','AMZN','ETP','CELG','EVHC','GT','HOG','ATI','GILD','CTL','NVDA','HBI','KKR','TPR','ICE','FDC','ON','WPM','AVGO','AABA','ABX','LB','CY','LYB','VIAB','KORS','CF','F','BIDU','SO','EPD','WLL','KMI','FB','JD','EQT','MGM','HLT','OKE','ARRY','FEYE','STM','IRM','TWTR','MOS','PTEN','UPS','DVN','GM','ALXN','OXY','RIO','MCD','LBTYA','TECK','MUR','MAR','BABA','NTAP','FCX','JNPR','GG','LBTYK','CAT','ETE','CBS','MAT','BHP','IBN','ATVI','RRC','KHC','AU','AMD','CPB','WMB','MRO','FOLD','CGNX','UAA','MDRX','VFC']
Mid_Weeklys = ['X','ROKU','NUE','SNAP','MT','ABBV','AMT','TRIP','EMR','CVS','AMAT','ABC','CAH','SU','WBA','MU','EXPE','DE','NKTR','ZTS','ESRX','PFE','WMT','UNH','JNJ','AEO','AFL','NOV','FOXA','NXPI','GE','HAL','DIS','DFS','LLY','LRCX','MYL','ABT','VRX','PCG','SYY','GSK','DHI','CSX','USB','HD','COF','ED','VZ','PHM','ADI','VOD','HRL','CTRP','EBAY','MMM','AET','AGNC','KSS','MOMO','WY','PM','IP','CSCO','MA','MRK','KO','MDT','WDC','XOM','TEVA','TSLA','BSX','AIG','HON','CZR','T','NLY','CL','KEY','YNDX','VLO','UNP','HES','CIEN','HPE','KMB','AXP','PG','MO','COP','MPC','WYNN','BK','LUV','DWDP','ORCL','MDLZ','FLEX','IBM','SLB','PYPL','PEP','ETN','APA','NKE','DISH','GS','AMGN','BMY','EOG','VALE','TXN','WFC','CC','CCL','ADM','BAX','AAL','SBUX','GPS','DB','DAL','BBY','MET','STX','LOW','CRM','HPQ','GLW','SWKS','AGN','MRVL','AZN','SYF','SCHW','AAPL','UAL','VIPS','C','CVX','KR','V','EA','COTY','BA','BX','SQ','AA','TGT','MS','BB','CTSH','SYMC','PBR','BP','DLTR','UTX','HIG','NFLX','TMUS','QCOM','COG','ADBE','SKX','PAA','MSFT','JPM','CMCSA','APC','BAC','M','NEM','INTC','CLR','AMZN','CELG','GT','HOG','GILD','CTL','NVDA','KKR','TPR','WPM','AVGO','AABA','ABX','LYB','VIAB','KORS','CF','F','BIDU','EPD','WLL','KMI','FB','JD','MGM','OKE','FEYE','TWTR','MOS','UPS','DVN','GM','ALXN','OXY','MCD','TECK','MAR','BABA','NTAP','FCX','JNPR','GG','CAT','ETE','CBS','MAT','ATVI','AMD','WMB','MRO','FOLD','UAA','VFC']

EOD_Stocks_of_interest = FinvizMidSized
EOD_Options_of_interest = Mid_Weeklys

# CONFIG _dicts_**************************************************************************
CONFIG_INTRADAY={
	# Lists of Stocks and Options to get
	'StockTicks_of_interest'	:Stocks_100_interest,
	'StockCandles_of_interest'	:Options_of_interest,
	'StockAverages_of_interest'	:combine_lists(Stocks_100_interest,EOD_Stocks_of_interest),
	'Options_of_interest'		:Options_of_interest,
	
	# Program Settings
	'main_loop_delay'			:0.02, # main loop time increment in seconds
	}

CONFIG_EOD={	
	# Lists of Stocks and Options to get
	'StockTicks_of_interest'	:combine_lists(Stocks_100_interest,EOD_Stocks_of_interest),
	'StockCandles_of_interest'	:combine_lists(Options_of_interest,EOD_Stocks_of_interest),
	'StockAverages_of_interest'	:combine_lists(Stocks_100_interest,EOD_Stocks_of_interest),
	'Options_of_interest'		:combine_lists(Options_of_interest,EOD_Options_of_interest),
	}

"""
CONFIG_TEMPLATE={	
	# Lists of Stocks and Options to get
	'StockTicks_of_interest'	:Stocks_100_interest,
	'StockCandles_of_interest'	:Options_of_interest,
	'Stocks_of_interest'		:combine_lists,
	'Options_of_interest'		:combine_lists,
	}
"""