''' convert to and from epoch time!
	Python2.7 doesn't explicitly handle epochtime well at all
	
	https://www.epochconverter.com/
	https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
'''
import time
from datetime import datetime

def to_UTCepoch(input):
	'''
		Takes datetime input down to the second returns int
		input = datetime.datetime(2018,02,16,11,0,0)
	'''
	input = input.replace(microsecond=0)
	return int(time.mktime(time.strptime(str(input), '%Y-%m-%d %H:%M:%S'))) - time.timezone

def to_LOCALepoch(input):
	'''
		similar to UTC epoch, but local time zone
		# same as time.time()
	'''
	input = input.replace(microsecond=0)
	return int(time.mktime(time.strptime(str(input), '%Y-%m-%d %H:%M:%S')))

def datetime_UTCepoch(year,month,day,hour,minute,second):
	'''
		converts datetime params into epoch
	'''
	input = datetime(year,month,day,hour,minute,second)
	return to_UTCepoch(input)

def UTCfrom_UTCepoch(UTCepoch):
	'''
		converts UTCepoch to UTC time
	'''
	return time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(int(UTCepoch)))

def LOCALfrom_UTCepoch(UTCepoch):
	'''
		converts UTCepoch to Local readable time
	'''
	return time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(int(UTCepoch)+time.timezone))

def NOW_epochMinute():
	# _perfect_min = datetime.now().replace(second=0, microsecond=0)
	# epoch_perfect_minute = epochtime.to_LOCALepoch(_perfect_min)
	
	return to_LOCALepoch(	datetime.now().replace(second=0, microsecond=0)	)

def NEXT_epochMinute():
	return NOW_epochMinute() + 60
	
# print UTCfrom_UTCepoch(1518931871)