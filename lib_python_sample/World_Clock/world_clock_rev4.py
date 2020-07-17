# Note: Epoch is in UTC https://stackoverflow.com/questions/23062515/do-unix-timestamps-change-across-timezones

# basics: https://www.geeksforgeeks.org/time-functions-in-python-set-1-time-ctime-sleep/
# Local means where the current_machine is located

# Using pytz
# All functions done naive (assume operatinos held in same timezone), convert using timedeltas not python's built-in apis
# Since all datetime and pytz which this is built on makes assumptions (assume nothing)
# we will pass all timezone nessacary information as arguments (by default, this library will remove timezone info off datetime object

# Goal:
# - remove need of Naive, localize, astimezone when handling time. Time doesn't care!
#	- Pytz, Naive, and localized datetime functions all grouped in it's own global section away from class.
#	- if changes occur to pytz, it's handled in it's own section!
# - to pass both datetime and timezone objects along with timezone at all times!,
# - all functions shall assume mix of naive-and-localized datetime inputs

# Change log:
#	2020-05-08		Added support for comparsion operators
#	2020-07-06		Changes type cast checks, added better functionality for creation from timedeltas
#	2020-07-07		Changed CONVERT_datetime_UTC so that if timezone included, will try to convert directly first,
#					changed subtraction to aware capable
#					changed __name__ to __str__ (string display functionaility)
#					Fixed DST issue when working with epoch days combined with time
#					Future work, includes cleaning up more DST default to only where it makes sense
#	2020-07-16		modified for windowshop
#					removing market clock references from prior role
#					removing unnecessary comments

import time
from datetime import datetime, timedelta, time as dt_time
if __name__ == "__main__":
	from timezone_table_rev3 import timezones, LOCAL_TIMEZONE, LOCAL_DAYLIGHT_OVERRIDE
else:
	from .timezone_table_rev3 import timezones, LOCAL_TIMEZONE, LOCAL_DAYLIGHT_OVERRIDE

# Datetime helper functions for string parsing and reading:
# a Paradyme (use ONLY these functions to translate back and forth)
def CONVERT_datetime_to_string(dt_obj):
	return dt_obj.strftime("%Y-%m-%d %H:%M:%S")

def CONVERT_string_to_datetime(dt_string):
	return datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")


# =================================================================================================
# PYTZ SECTION

# Datetime Normalization
# Datetime by default grabs system time without getting local timezone
# **Everything** MUST be normalized to real UTC, system maybe moved into different timezone!

def STATUS_DAYLIGHT_SAVINGS(timezone = LOCAL_TIMEZONE):
	# returns the CURRENT daylight STATUS from any timezone in the world specified in timezone_table directory
	# timezone = LOCAL_TIMEZONE (default), assume asking of local system time
	
	# https://docs.python.org/3/library/time.html#time.localtime
	# return (time.localtime().tm_isdst > 0) << this uses local_machine setting (bad for servers)
	# This is calculated from computer timezone, and servers will have issues: https://stackoverflow.com/questions/2881025/python-daylight-savings-time
	
	# Synced to internet time (REAL UNIVERSAL TIME), Naive
	utc_dt_now = datetime.utcnow()
	
	# convert to timezone of interest
	timezone_dt_now = timezones[timezone].localize(utc_dt_now, is_dst=None)
	return (timezone_dt_now.tzinfo._dst.seconds > 0)
	
def CHECK_DAYLIGHT_SAVINGS_UTC(dt_obj, timezone = LOCAL_TIMEZONE):
	# https://stackoverflow.com/questions/2881025/python-daylight-savings-time
	timezone_dt_obj = CONVERT_UTC_to_local(dt_obj, timezone=timezone)
	return (timezone_dt_obj.tzinfo._dst.seconds > 0)
	
def CHECK_DAYLIGHT_SAVINGS_LOCALIZED(dt_obj):
	# this only returns if properly localized
	return (dt_obj.tzinfo._dst.seconds > 0)
	
def LOCAL_DAYLIGHT(timezone = LOCAL_TIMEZONE):
	if LOCAL_DAYLIGHT_OVERRIDE == None:
		return STATUS_DAYLIGHT_SAVINGS(timezone)
	return LOCAL_DAYLIGHT_OVERRIDE

def SET_naive_datetime(dt_obj):
	return dt_obj.replace(tzinfo=None)

# Using pytz object to convert timezones to UTC
def TEASE_datetime_UTC(dt_obj, *args, **kwargs):
	# May break, if timezone not configured properly
	return dt_obj.astimezone(timezones["UTC"])

def CONVERT_datetime_UTC(dt_obj, timezone = LOCAL_TIMEZONE, DST = LOCAL_DAYLIGHT(), *args, **kwargs):
	# quick return, less calculation if already UTC
	if timezone == "UTC":
		return dt_obj.replace(tzinfo=timezones["UTC"])
	elif type(dt_obj.tzinfo) == type(timezones["UTC"]):
		return dt_obj
	
	if not dt_obj.tzinfo == None:
		try:
			# if localized already, try astimezone directly
			# this differs from LOCALIZE_datetime, DO NOT COMBINE (timezone_incoming, vs timezone_outgoing in localize function)
			return dt_obj.astimezone(timezones["UTC"])
		except:
			print("Warning: World_Clock.Timestamp module uses pytz backend, please adjust datetime objects as needed, or unintended dates may occur")
	
	# All else fails, Forces dt_obj directly into desired timezone denovo
	# 1) Force Naive timezone
	naive_dt = SET_naive_datetime(dt_obj)
	
	# 2) set timezone to timezone specified
	localized_dt = timezones[timezone].localize(naive_dt, is_dst = DST)
	# 3) return UTC datetime object
	return localized_dt.astimezone(timezones["UTC"])
	
def CONVERT_timezone(dt_obj, start_timezone, end_timezone, DST = LOCAL_DAYLIGHT(), *args, **kwargs):
	# 1) Force Naive timezone
	naive_dt = SET_naive_datetime(dt_obj)
	
	# set starting timezone
	localized_dt = timezones[start_timezone].localize(naive_dt, is_dst=DST)
	
	# set endiing timezone
	return localized_dt.astimezone(timezones[end_timezone])
	
def CONVERT_UTC_to_local(datetime_object, timezone = LOCAL_TIMEZONE, *args, **kwargs):
	# Inverse of convert_datetime_UTC
	# Assumes datetime_object is in UTC_timezone by default
	dt_obj = datetime_object.replace(tzinfo=timezones["UTC"])
	return dt_obj.astimezone(timezones[timezone])
	
def LOCALIZE_datetime(dt_obj, timezone = LOCAL_TIMEZONE, DST = LOCAL_DAYLIGHT(), *args, **kwargs):
	# Attempts to relocalize timezone of datetime_object to provided timezone param
	# Try simple check if already correct timezone
	if type(dt_obj.tzinfo) == type(timezones[timezone]):
		return dt_obj
	
	# If localized already, try astimezone directly
	if not dt_obj.tzinfo == None:
		try:
			return dt_obj.astimezone(timezones[timezone])
		except:
			print("Warning: World_Clock.Timestamp module uses pytz backend, please adjust datetime objects as needed, or unintended dates may occur")
	
	# All else fails, Forces dt_obj directly into desired timezone denovo
	# 1) Force Naive timezone
	naive_dt = SET_naive_datetime(dt_obj)
	
	# 2) Localize naive to timezone
	return timezones[timezone].localize(naive_dt, is_dst = DST)

# END PYTZ SECTION
# =================================================================================================


# =================================================================================================
# Epoch Helper
# Helper functions to get value from datetime object since UTC epoch
UTC_epoch = datetime.utcfromtimestamp(0).replace(tzinfo=timezones["UTC"])
# _TD_zero = timedelta(0)
# _time_zero = dt_time()

def GET_timedelta_since_epoch(dt_obj, *args, **kwargs):
	UTC_dt_obj = CONVERT_datetime_UTC(dt_obj, *args, **kwargs)
	return UTC_dt_obj - UTC_epoch

def GET_datetime_epoch_seconds(dt_obj, *args, **kwargs):
	epoch_delta = GET_timedelta_since_epoch(dt_obj, *args, **kwargs)
	return int(epoch_delta.total_seconds())

def GET_datetime_epoch_minutes(dt_obj, *args, **kwargs):
	epoch_seconds = GET_datetime_epoch_seconds(dt_obj, *args, **kwargs)
	return epoch_seconds//60

def GET_datetime_epoch_hours(dt_obj, *args, **kwargs):
	epoch_seconds = GET_datetime_epoch_seconds(dt_obj, *args, **kwargs)
	return epoch_seconds//3600
	
def GET_datetime_epoch_days(dt_obj, *args, **kwargs):
	epoch_delta = GET_timedelta_since_epoch(dt_obj, *args, **kwargs)
	return int(epoch_delta.days)

# =================================================================================================
# Local Helper
# Helper functions to get value from any datetime object
naive_epoch = datetime.utcfromtimestamp(0)

def GET_timedelta_since_local_epoch(dt_obj, timezone=LOCAL_TIMEZONE, DST=LOCAL_DAYLIGHT(), *args, **kwargs):
	local_dt_obj = LOCALIZE_datetime(dt_obj, timezone=timezone, DST=DST, *args, **kwargs)
	local_epoch = LOCALIZE_datetime(naive_epoch, timezone=timezone, DST=DST, *args, **kwargs)
	return local_dt_obj- local_epoch

def GET_datetime_local_seconds(dt_obj, *args, **kwargs):
	epoch_delta = GET_timedelta_since_local_epoch(dt_obj, *args, **kwargs)
	return int(epoch_delta.total_seconds())
	
def GET_datetime_local_minutes(dt_obj, *args, **kwargs):
	epoch_seconds = GET_datetime_local_seconds(dt_obj, *args, **kwargs)
	return epoch_seconds//60

def GET_datetime_local_hours(dt_obj, *args, **kwargs):
	epoch_seconds = GET_datetime_local_seconds(dt_obj, *args, **kwargs)
	return epoch_seconds//3600
	
def GET_datetime_local_days(dt_obj, *args, **kwargs):
	epoch_delta = GET_timedelta_since_local_epoch(dt_obj, *args, **kwargs)
	return int(epoch_delta.days)
	
def GET_local_second_of_day(dt_obj, timezone=LOCAL_TIMEZONE, DST=LOCAL_DAYLIGHT(), *args, **kwargs):
	local_dt_obj = LOCALIZE_datetime(dt_obj, timezone=timezone, DST=DST, *args, **kwargs)
	hours = local_dt_obj.hour
	minutes = local_dt_obj.minute
	seconds = local_dt_obj.second
	return (3600*hours) + (60*minutes) + seconds
	
def GET_local_minute_of_day(dt_obj, timezone=LOCAL_TIMEZONE, DST=LOCAL_DAYLIGHT(), *args, **kwargs):
	local_dt_obj = LOCALIZE_datetime(dt_obj, timezone=timezone, DST=DST, *args, **kwargs)
	hours = local_dt_obj.hour
	minutes = local_dt_obj.minute
	return (60*hours) + minutes
	
def GET_local_hour_of_day(dt_obj, timezone=LOCAL_TIMEZONE, DST=LOCAL_DAYLIGHT(), *args, **kwargs):
	local_dt_obj = LOCALIZE_datetime(dt_obj, timezone=timezone, DST=DST, *args, **kwargs)
	return local_dt_obj.hour

# =================================================================================================
# Localized Helper
# Helper functions to get value from ALREADY localized datetime objects, use with CAUTION
# Timezone information STILL needs to be passed in, but daylight-savings-time is irrelvent
def GET_timedelta_since_localized_epoch(dt_obj, timezone=LOCAL_TIMEZONE, *args, **kwargs):
	local_epoch = LOCALIZE_datetime(naive_epoch, timezone=timezone, *args, **kwargs)
	return dt_obj- local_epoch

def GET_datetime_localized_seconds(dt_obj, *args, **kwargs):
	epoch_delta = GET_timedelta_since_localized_epoch(dt_obj, *args, **kwargs)
	return int(epoch_delta.total_seconds())
	
def GET_datetime_localized_minutes(dt_obj, *args, **kwargs):
	epoch_seconds = GET_datetime_localized_seconds(dt_obj, *args, **kwargs)
	return epoch_seconds//60

def GET_datetime_localized_hours(dt_obj, *args, **kwargs):
	epoch_seconds = GET_datetime_localized_seconds(dt_obj, *args, **kwargs)
	return epoch_seconds//3600
	
def GET_datetime_localized_days(dt_obj, *args, **kwargs):
	epoch_delta = GET_timedelta_since_localized_epoch(dt_obj, *args, **kwargs)
	return int(epoch_delta.days)
	
def GET_localized_second_of_day(dt_obj, *args, **kwargs):
	hours = dt_obj.hour
	minutes = dt_obj.minute
	seconds = dt_obj.second
	return (3600*hours) + (60*minutes) + seconds
	
def GET_localized_minute_of_day(dt_obj, *args, **kwargs):
	hours = dt_obj.hour
	minutes = dt_obj.minute
	return (60*hours) + minutes
	
def GET_localized_hour_of_day(dt_obj, *args, **kwargs):
	return dt_obj.hour
	
# =================================================================================================
# UTC relative functions (UTC epoch reference)
def GET_seconds_since_epoch():
	return int(time.time()) # UTC relative
	
def GET_days_since_epoch():
	return time.time()//86400 # UTC relative

# =================================================================================================
# Time objecs need NOT be the same! But are HIGHLY contextual!
def CALC_timedelta_difference(dtobj_A, dtobj_B, *args, **kwargs):
	if not type(dtobj_A) == type(dtobj_B):
		raise TypeError("Objects dtobj_A and dtobj_B, must both be of same datetime objects")
	return dtobj_A-dtobj_B

def CALC_difference_seconds(*args, abs=False, **kwargs):
	td_difference = CALC_timedelta_difference(*args, **kwargs)
	if abs:
		return abs(int(td_difference.total_seconds()))
	else:
		return int(td_difference.total_seconds())

def CALC_difference_minutes(*args, abs=False, **kwargs):
	td_seconds = CALC_difference_seconds(*args, **kwargs)
	if abs:
		return abs(int(td_seconds/60))
	else:
		return int(td_seconds/60)

def CALC_difference_hours(*args, abs=False, **kwargs):
	td_seconds = CALC_difference_seconds(*args, **kwargs)
	if abs:
		return abs(int(td_seconds/3600))
	else:
		return int(td_seconds/3600)
		
def CALC_difference_days(*args, abs=False, **kwargs):
	td_seconds = CALC_difference_seconds(*args, **kwargs)
	if abs:
		return abs(int(td_seconds/86400))
	else:
		return int(td_seconds/86400)

# =================================================================================================

#/* DOCUMENTATION
#Methods of defining a timestamp (Goal is to define UTC first!):
#	1) No info given, Timestamp()				>> UTC from utcnow, set timezone to assumed timezone, or given as timezone kwargs
#		Timestamp('now'), Now,
#		Timestamp(None), etc.
#	
#	2) Datetime obj
#	naive datetime obj + timezone + DST		>> UTC from (datetime + timezone + DST)
#	naive datetime obj + timezone			>> UTC from (datetime + timezone + assumed DST)
#	naive datetime obj						>> UTC from (datetime + assumed timezone + assumed DST)
#	
#	# Extract timezone when able ( we assume if timezone info available, user understands datetime timezones), Raise warning when unable to extract timezone when localized > treat as naive
#	# Assume timezone is UNKNOWN (NAIVE), disregard datetime's handling of timezone as it's not supported
#	localized datetime obj with proper tzinfo:
#		+ timezone + DST					>> UTC from (extracted datetime), set change timezone, discard DST
#		+ timezone							>> UTC from (extracted datetime), set change timezone,
#		+ none								>> UTC from (extracted datetime), same timezone (default)
#	
#	localized datetime obj with failed tzinfo: >> default to naieve datetime obj method 
#	
#	3) Timedelta_object
#	timedelta_object + timezone				>> convert local epoch to timezone add timedelta for local_timezone, convert to UTC, set local timezone
#	timedelta_object						>> conver to assumed epoch timezone, add, convert to UTC
#	
#	4) Year, Month, Day, 24-Hour, 60-minute, seconds, milliseconds, timezone, DST
#		Timezone/DST assumed if not specified
#		Create naive datetime from year, month, day, hour, etc.
#		Pass into Datetime object method
#	
#	**	DST info is used only to set initial UTC datetime
#			Discarded after UTC set
#			can be referenced through GET_DST(): gets localized datetime_object, gets DST flag.
#		Timezone and DST is always optional keyword arguement passed in
#			Assume timezone and DST to be default if not specified
#		
#	EXAMPLE creation:
#		1)	Timestamp(), Timestamp('Now'), Timestamp('now' [, timezone, DST_true/false])	[optional]
#		2)	Timestamp(datetime_obj [, timezone, DST_true/false])	[optional]
#		3)	Timestamp(Timedelta [, timezone]) [optional]
#		4)	Timestamp(Year [, Month, Day, hours, minute, second, milliseconds, microseconds] etc, [, timezone, DST_true/false])	[optional]
#			Timestamp( (Year [, Month, Day, hours, minute,),  [, timezone, DST_true/false])	[optional]
#			Timestamp( [Year [, Month, Day, hours, minute,],  [, timezone, DST_true/false])	[optional]
#			Timestamp(Year=XXXX, etc, [, timezone, DST_true/false])	[optional]
#	
#	=========================================================
#Implementation:
#	Optional keyword arguments in header
#		set self.timezone
#		
#	Count number of arguments
#		if 0: Default
#			if "Year" key in kwargs:
#				collect Year, month, day etc.
#				4) Timestamp(Year)
#			else:
#				1) Timestamp()
#		elif arg[0] == type('str'):
#			1) Timestamp()
#		elif arg[0] == datetime_obj:
#			2) Timestamp(datetime_obj)
#		elif arg[0] == timedelta_object:
#			3) Timestamp(Timedelta)
#		elif arg[0] == type(int) or == () or []:
#			# Extract year, month, etc.
#			if arg[0] == type(int):
#				iterate args
#			else:
#				iterate () or []
#			4) Timestamp(Year)
#		
#		# Else		
#		raise exception: timeformat error
#
#		**	Pass in keyword args
#*/

class Timestamp():
	# Attributes
	timezone = "UTC"
	local_timezone = "UTC"
	
	# Both are aware datetimes
	local_datetime = None # cached
	UTC_datetime = None
	
	def __init__(self, *args, timezone=LOCAL_TIMEZONE, DST = LOCAL_DAYLIGHT(), **kwargs):
		# Adding timezone, DST into into kwargs header
		kwargs["timezone"] = timezone
		kwargs["DST"] = DST
		self.timezone = timezone
		self.local_timezone = timezone
		
		if len(args) == 0:
			if "year" in kwargs:
				self.INITIATE_tuple(**kwargs)
			elif "days" in kwargs:
				# initiated with number of days since local epoch
				self.INITIATE_day_num(**kwargs)
			else:
				self.INITIATE_now(**kwargs)
		
		elif len(args)==1 and type(args[0])==int:
			# initiated with number of days since local epoch
			self.INITIATE_day_num(days=args[0],**kwargs)
		
		elif type(args[0]) == str:
			self.INITIATE_now(**kwargs)
		
		elif type(args[0]) == type(naive_epoch):
			self.INITIATE_datetime(*args, **kwargs)
		
		elif type(args[0]) == timedelta:
			self.INITIATE_timedelta(*args, **kwargs)
			
		elif type(args[0])==int or type(args[0])==type((None,)) or type(args[0])==type([None,]):
			# Making timestamp using time attribute list.
			standard_time_list = [] # [False * 7], faster to append, so we're appending (practice)
			
			# Iterate over args
			if type(args[0])==type(1):
				# Check length
				arg_length = len(args)
				if arg_length > 7:
					raise ValueError("Too many time arguemnts, limited to 7 arguements [year, month, day, hour, minute, second, microsecond]")
				for i in range(7):
					#for each element of args:
					if i < arg_length:
						if not (type(args[i]) == type(1)):
							raise TypeError("Time arguements must be of type(int)")
						standard_time_list.append(args[i])
					else:
						standard_time_list.append(False)
						
			# Iterate over tuple
			elif type(args[0])==type((None,)):
				arg_tuple = args[0]
				arg_length = len(arg_tuple)
				if arg_length > 7:
					raise ValueError("Too many time arguemnts, limited to 7 arguements [year, month, day, hour, minute, second, microsecond]")
				for i in range(7):
					#for each element of arg_tuple:
					if i < arg_length:
						if not (type(arg_tuple[i]) == type(1)):
							raise TypeError("Time arguements must be of type(int)")
						standard_time_list.append(arg_tuple[i])
					else:
						standard_time_list.append(False)
						
			# Iterate over list
			elif type(args[0])==type([None,]):
				arg_list = args[0]
				arg_length = len(arg_list)
				
				if arg_length > 7:
					raise ValueError("Too many time arguemnts, limited to 7 arguements [year, month, day, hour, minute, second, microsecond]")
				for i in range(7):
					#for each element of arg_list:
					if i < arg_length:
						if not (type(arg_list[i]) == type(1)):
							raise TypeError("Time arguements must be of type(int)")
						standard_time_list.append(arg_list[i])
					else:
						standard_time_list.append(False)
			
			# Create time object to pass into self.INITIATE_tuple()
			if standard_time_list[0]:
				kwargs['year'] = standard_time_list[0]
			if standard_time_list[1]:
				kwargs['month'] = standard_time_list[1]
			if standard_time_list[2]:
				kwargs['day'] = standard_time_list[2]
			if standard_time_list[3]:
				kwargs['hour'] = standard_time_list[3]
			if standard_time_list[4]:
				kwargs['minute'] = standard_time_list[4]
			if standard_time_list[5]:
				kwargs['second'] = standard_time_list[5]
			if standard_time_list[6]:
				kwargs['millisecond'] = standard_time_list[6]
			
			# Pass kwargs into initiation function
			self.INITIATE_tuple(**kwargs)
			
		else:
			raise ValueError("Timeformat error, see world_clock.Timestamp Documentation")
		
	def INITIATE_now(self, timezone=LOCAL_TIMEZONE, **kwargs):
		# https://stackoverflow.com/questions/62151/datetime-now-vs-datetime-utcnow
		naive_now_datetime = datetime.utcnow() # utcnow() is ~30x faster than now()
		self.UTC_datetime = CONVERT_datetime_UTC(naive_now_datetime, timezone='UTC')
		self.CHANGE_timezone(timezone)
	
	def INITIATE_datetime(self, *args, **kwargs):
		self.INITIATE_naive_datetime(*args, **kwargs)
		
	def INITIATE_naive_datetime(self, naive_datetime, timezone=LOCAL_TIMEZONE, DST=LOCAL_DAYLIGHT(), **kwargs):
		# Convert into UTC first, caller should know if DST
		self.UTC_datetime = CONVERT_datetime_UTC(naive_datetime, timezone=timezone, DST=DST, **kwargs)
		# Convert to local last
		self.CHANGE_timezone(timezone)
		
	def INITIATE_timedelta(self, timedelta_obj, timezone=LOCAL_TIMEZONE, **kwargs):
		# This is relative to localized epoch in current timezone, must start in local frame first
		local_epoch = LOCALIZE_datetime(naive_epoch, timezone=timezone, **kwargs)
		local_datetime = local_epoch + timedelta_obj
		
		# Convert to UTC
		#	DTS is UNKNOWN since passing in DST arguement, Note need to change kwargs since it wasn't pulled initially
		#	However, we can guarentee an absolute reference since local epoch is 100% properly localized,
		#		we can run the DST finding function
		kwargs["DST"] = CHECK_DAYLIGHT_SAVINGS_LOCALIZED(local_datetime)
		self.UTC_datetime = CONVERT_datetime_UTC(local_datetime, timezone=timezone, **kwargs)
		
		# Convert to local
		self.CHANGE_timezone(timezone)
		
	def INITIATE_day_num(self, timezone=LOCAL_TIMEZONE, time=None, days=0, hours=0, minutes=0, weeks=0, seconds=0, milliseconds=0, microseconds=0, **kwargs):
		# Obsolete - is affected by DST
		# timedelta_obj = timedelta(days=days, hours=hours, minutes=minutes, weeks=weeks, seconds=seconds, milliseconds=milliseconds, microseconds=microseconds )
		# self.INITIATE_timedelta(timedelta_obj, timezone=timezone, **kwargs)
		# print('day_num, triggered')
		# New method
		# Use local_epoch, add days. Then use date() and (time() or timedelta)
		timedelta_days = timedelta(days=days)
		# kwargs['DST'] = False # To help if world transistions away from DST
		local_date = LOCALIZE_datetime(naive_epoch, timezone=timezone, **kwargs) + timedelta_days # Sets correct date(), timezone (but wrong DST!), will need to 
		local_date = local_date.astimezone(timezones[timezone])	# small bug to work around (goes to show better to work in UTC)
		
		# Now to set correct time of day and write to self.UTC_datetime
		if time == None:
			# Use Timedelta (must set initial time to zero)
			local_date = datetime.combine(local_date.date(), dt_time(), tzinfo = local_date.tzinfo)
			timedelta_obj = timedelta(hours=hours, minutes=minutes, weeks=weeks, seconds=seconds, milliseconds=milliseconds, microseconds=microseconds)
			self.UTC_datetime = CONVERT_datetime_UTC(local_date + timedelta_obj, timezone=timezone, **kwargs)
		
		else: # Use combine on date, time, directly
			local_datetime = datetime.combine(local_date.date(), time, tzinfo = local_date.tzinfo)
			self.UTC_datetime = CONVERT_datetime_UTC(local_datetime, timezone=timezone, **kwargs)
		
		# Convert to local
		self.CHANGE_timezone(timezone)
		
	def INITIATE_tuple(self, year=1970, month=1, day=1, hour=0, minute=0, second=0, microsecond=0, timezone=LOCAL_TIMEZONE, DST=LOCAL_DAYLIGHT(), **kwargs):
		# Create datetime
		naive_datetime = datetime(year, month, day, hour, minute, second, microsecond)
		# Pass into datetime initation method
		self.INITIATE_naive_datetime(naive_datetime, timezone=timezone, DST=DST, **kwargs)
		
	# ==============================================================================================
	# SELF REFERENCE STATES
	# Changed from version 2:
	# Stored Datetimes are now timezone aware WITHIN timestamp instance
	def GET_datetime_local(self, timezone=None):
		# Check if cached
		if timezone==None or timezone==self.local_timezone:
			return self.local_datetime
		# Else Calculate
		return CONVERT_UTC_to_local(self.UTC_datetime, timezone=timezone)
		
	def CHANGE_timezone(self, timezone=None):
		if timezone==None:
			# timezone = self.local_timezone # actually no action needed, if no timzone change actually occuring
			return self.local_datetime
		
		# Force a timezone recalculation
		self.local_datetime = CONVERT_UTC_to_local(self.UTC_datetime, timezone=timezone)
		self.timezone = timezone
		self.local_timezone = timezone
		self.DST = CHECK_DAYLIGHT_SAVINGS_UTC(self.UTC_datetime, timezone=timezone) # Should never be passed forward, only here for quick reference
		return self.local_datetime
	
	# --------------------------------------------------------------
	# Datetime transparency
	def weekday(self, *args, **kwargs):
		local_datetime = self.GET_datetime_local(*args, **kwargs)
		return local_datetime.weekday()
		
	def local_date(self, *args, **kwargs):
		local_datetime = self.GET_datetime_local(*args, **kwargs)
		return local_datetime.year, local_datetime.month, local_datetime.day
	
	def strftime(self, *args, **kwargs):
		return self.GET_datetime_local().strftime(*args, **kwargs)
	
	def time(self, *args, **kwargs):
		local_datetime = self.GET_datetime_local(*args, **kwargs)
		return local_datetime.time()
		
	def today(self, *args, **kwargs):
		# returns datetime.date() object
		local_datetime = self.GET_datetime_local(*args, **kwargs)
		return local_datetime.today()
		
	def local_epoch_day(self, *args, **kwargs):
		return self.GET_datetime_local_days(*args, **kwargs)
	
	def local_hour(self, *args, **kwargs):
		return self.GET_local_hour_of_day(*args, **kwargs)
	
	def local_minute(self, *args, **kwargs):
		return self.GET_local_minute_of_day(*args, **kwargs)
		
	def local_second(self, *args, **kwargs):
		return self.GET_local_second_of_day(*args, **kwargs)
		
	def utc_epoch_day(self, *args, **kwargs):
		return GET_datetime_epoch_days(self.UTC_datetime, timezone="UTC")
	
	# ================================================================================================
	# OVERLOAD and INTERNAL FUNCTIONS
	def __str__(self):
		return str(self.local_datetime)
	
	@staticmethod
	def _gen_timestamp_fromUTC(UTC_datetime, timezone=LOCAL_TIMEZONE):
		# internal function that creates a new timestamp using UTC_datetime, and a desired local_timezone
		new_timestamp = Timestamp(UTC_datetime, timezone="UTC")
		new_timestamp.CHANGE_timezone(timezone)
		return new_timestamp
	
	# --------------------------------------------------------------
	# Check object types
	@staticmethod
	def _check_timedelta_error( time_object):
		if not type(time_object)==timedelta:
			raise TypeError("time_object can only operate on datetime.timedelta objects, not datetime.datetime")
		return True
		
	@staticmethod
	def _check_datetime_error( time_object):
		if not type(time_object)==type(UTC_epoch):
			raise TypeError("time_object can only operate on datetime.datetime objects, not datetime.timedelta")
		return True
	
	@staticmethod
	def _check_timedelta( time_object):
		return type(time_object) == timedelta
	
	@staticmethod
	def _check_datetime( time_object):
		return type(time_object) == type(UTC_epoch)
	
	@staticmethod
	def _check_timestamp( time_object):
		return type(time_object) == Timestamp
	
	@staticmethod
	def _check_dt_time( time_object):
		return type(time_object) == dt_time
	
	# --------------------------------------------------------------
	# Operator overload	
	def __sub__(self, time_object, *args, **kwargs):
		# timestamp - DATETIME = timedelta DONE
		if self._check_datetime(time_object):
			return self._sub_datetime(time_object, *args, **kwargs)
		
		# timestamp - TIMEDELTA = new timestamp DONE
		if self._check_timedelta(time_object):
			return self._sub_timedelta(time_object, *args, **kwargs)
			
		# timestamp - TIMESTAMP = timedelta DONE
		if self._check_timestamp(time_object):
			return self._sub_timestamp(time_object, *args, **kwargs)
			
		# timestamp - DT_TIME = timedelta DONE
		if self._check_dt_time(time_object):
			return self._sub_dt_time(time_object, *args, **kwargs)
		
		# else
		raise TypeError("Can only subtract Types(datetime, timedelta, timestamp, datetime.time()) from Timestamp object, instead received type (on-right): " + str(type(time_object)) )
	
	def __rsub__(self, time_object, *args, **kwargs):
		# For the most part this can provide the negative of __sub__ (reverse) for all operations
		# except for TIMEDELTA - timestamp = not defined
		
		# DATETIME - timestamp = timedelta DONE
		if self._check_datetime(time_object):
			return -self._sub_datetime(time_object, *args, **kwargs)
			
		# TIMESTAMP - timestamp = timedelta DONE
		if self._check_timestamp(time_object):
			return -self._sub_timestamp(time_object, *args, **kwargs)
			
		# DT_TIME - timestamp = timedelta DONE
		if self._check_dt_time(time_object):
			return -self._sub_dt_time(time_object, *args, **kwargs)
		
		raise TypeError("Can only subtract Timstamp from time-types(datetime, timestamp, datetime.time()), instead received type (on-left): " + str(type(time_object)) )
	
	def __add__(self, time_object, *args, **kwargs):
		# timestamp + TIMEDELTA only = timestamp DONE
		if self._check_timedelta_error(time_object):
			return self._add_timedelta(time_object, *args, **kwargs)
			
		raise TypeError("Can only add Type(timedelta), instead received type: " + str(type(time_object)) )
	# Time add operations are comatorical
	__radd__ = __add__
	
	def __eq__(self, time_object, *args, **kwargs):
		# timestamp == DATETIME : T/F
		if self._check_datetime(time_object):
			return self._eq_datetime(time_object, *args, **kwargs)
			
		# timestamp == TIMESTAMP : T/F
		if self._check_timestamp(time_object):
			return self._eq_timestamp(time_object, *args, **kwargs)
			
		# timestamp == DT_TIME : T/F
		if self._check_dt_time(time_object):
			return self._eq_dt_time(time_object, *args, **kwargs)
			
		raise TypeError("Can only equate Timstamp to time-types(datetime, timestamp, datetime.time()), instead received type(right-side): " + str(type(time_object)) )

	def __lt__(self, time_object, *args, **kwargs):
		# timestamp < DATETIME : T/F
		if self._check_datetime(time_object):
			return self._lt_datetime(time_object, *args, **kwargs)
			
		# timestamp < TIMESTAMP : T/F
		if self._check_timestamp(time_object):
			return self._lt_timestamp(time_object, *args, **kwargs)
			
		# timestamp < DT_TIME : T/F
		if self._check_dt_time(time_object):
			return self._lt_dt_time(time_object, *args, **kwargs)
			
		raise TypeError("Can only compare Timstamp to time-types(datetime, timestamp, datetime.time()), instead received type(right-side): " + str(type(time_object)) )
	
	def __gt__(self, time_object, *args, **kwargs):
		# timestamp > DATETIME : T/F
		if self._check_datetime(time_object):
			return self._gt_datetime(time_object, *args, **kwargs)
			
		# timestamp > TIMESTAMP : T/F
		if self._check_timestamp(time_object):
			return self._gt_timestamp(time_object, *args, **kwargs)
			
		# timestamp > DT_TIME : T/F
		if self._check_dt_time(time_object):
			return self._gt_dt_time(time_object, *args, **kwargs)
			
		raise TypeError("Can only compare Timstamp to time-types(datetime, timestamp, datetime.time()), instead received type(right-side): " + str(type(time_object)) )
	
	def __ne__(self, *args, **kwargs):
		return not self.__eq__(*args, **kwargs)
	def __ge__(self, *args, **kwargs):
		return not self.__lt__(*args, **kwargs)
	def __le__(self, *args, **kwargs):
		return not self.__gt__(*args, **kwargs)
	
	def _utc_normalize_datetime(self, time_object, *args, **kwargs):
		# For sake of operations, normalize the time_object to localized (convert if naive)
		# 1) Check if timezone information is *not  avaiable(if naive)
		if time_object.tzinfo == None:
			# Then assume same timezone
			return CONVERT_datetime_UTC(time_object, timezone = self.local_timezone, DST = self.DST)
		
		# 2) Otherwise timezone information is avaiable, do straight return original UTC_datetime (datetime_object)
		return time_object
	
	# --------------------------------------------------------------
	# sub operators (returns timestamp OR timedelta), will not return datetime since more power in timestamp than datetime
	def _sub_datetime(self, time_object, *args, **kwargs):
		# time_object = datetime >> return timedelta
		utc_time_object = self._utc_normalize_datetime(time_object, *args, **kwargs)
		return self.UTC_datetime - utc_time_object
		
	def _sub_timestamp(self, time_object, *args, **kwargs):
		# time_object = timestamp >> return timedelta
		return self.UTC_datetime - time_object.UTC_datetime
		
	def _sub_timedelta(self, time_object, *args, **kwargs):
		# time_object = timedelta >> return timestamp
		new_UTC_datetime = self.UTC_datetime - time_object
		return self._gen_timestamp_fromUTC(new_UTC_datetime, timezone = self.local_timezone)
		
	def _sub_dt_time(self, time_object, *args, **kwargs):
		# time_object = datetime.time() >> return timedelta (on same day)
		# https://stackoverflow.com/questions/5259882/subtract-two-times-in-python
		# dummy_date = self.UTC_datetime.date()
		# input_dt = datetime.combine(dummy_date,time_object)
		# return SET_naive_datetime(self.UTC_datetime) - input_dt
		return self.subtract(time_object, *args, **kwargs)
	
	def subtract(self, time_object, *args, **kwargs):
		# **kwargs allows DST to be passed in to differentiate ambuguitys such as forex 24 hour.
		# ie, obj_timedelta = timestamp_obj.sub(datetime.time, DST=False), though auto-assumes same timezone
		if 'DST' in kwargs:
			if not lower(kwargs['DST']) == 'auto':
				input_dt = datetime.combine(self.local_datetime.date(),time_object)
				input_dt = LOCALIZE_datetime(input_dt, timezone=timezone, **kwargs)
				return self.local_datetime - input_dt
		
		# otherwise ASSUME same DST settings
		input_dt = datetime.combine(self.local_datetime.date(),time_object, tzinfo=self.local_datetime.tzinfo)
		return self.local_datetime - input_dt
	# duplicate names
	sub=subtract
	
	# --------------------------------------------------------------
	# add operators
	def _add_timedelta(self, time_object, *args, **kwargs):
		# time_object = timedelta >> return timestamp
		new_UTC_datetime = self.UTC_datetime + time_object
		return self._gen_timestamp_fromUTC(new_UTC_datetime, timezone = self.local_timezone)
		
	# --------------------------------------------------------------
	# comparison operators (timestamp, datetime, DT_TIME)
	# equal(==)
	def _eq_datetime(self, time_object, *args, **kwargs):
		utc_time_object = self._utc_normalize_datetime(time_object, *args, **kwargs)
		return (self.UTC_datetime == utc_time_object)
		
	def _eq_timestamp(self, time_object, *args, **kwargs):
		return (self.UTC_datetime == time_object.UTC_datetime)
	
	def _eq_dt_time(self, time_object, *args, **kwargs):
		# local time assumed
		return (self.time() == time_object)
	
	# less than(<)
	def _lt_datetime(self, time_object, *args, **kwargs):
		utc_time_object = self._utc_normalize_datetime(time_object, *args, **kwargs)
		return self.UTC_datetime < utc_time_object
		
	def _lt_timestamp(self, time_object, *args, **kwargs):
		return self.UTC_datetime < time_object.UTC_datetime
	
	def _lt_dt_time(self, time_object, *args, **kwargs):
		# local time assumed
		return self.time() < time_object
	
	# greater than(>)
	def _gt_datetime(self, time_object, *args, **kwargs):
		utc_time_object = self._utc_normalize_datetime(time_object, *args, **kwargs)
		return self.UTC_datetime > utc_time_object
		
	def _gt_timestamp(self, time_object, *args, **kwargs):
		return self.UTC_datetime > time_object.UTC_datetime
	
	def _gt_dt_time(self, time_object, *args, **kwargs):
		# local time assumed
		return self.time() > time_object
	
	# ================================================================================================
	# import / export serialization
	def _export(self):
		export_dict = {
			"local_datetime": CONVERT_datetime_to_string(self.local_datetime),
			"timezone"		: self.local_timezone,
			"DST"			: self.DST,
			"UTC_datetime"	: CONVERT_datetime_to_string(self.UTC_datetime),
		}
		return export_dict
	
	@staticmethod
	def _import(config):
		# really only need UTC and timezone to import successfully
		local_timezone = config["timezone"]
		str_utc_datetime = config["UTC_datetime"]
		new_utc_datetime = CONVERT_string_to_datetime(str_utc_datetime)
		imported_timestamp = Timestamp._gen_timestamp_fromUTC(new_utc_datetime, timezone=local_timezone)
		return imported_timestamp
	
	# ================================================================================================
	# UTC CONVERSIONS CALULATIONS
	def GET_datetime_UTC(self):
		return self.UTC_datetime
		
	def GET_datetime_epoch_seconds(self):
		return GET_datetime_epoch_seconds(self.UTC_datetime, timezone="UTC")
	def GET_datetime_epoch_minutes(self):
		return GET_datetime_epoch_minutes(self.UTC_datetime, timezone="UTC")
	def GET_datetime_epoch_hours(self):
		return GET_datetime_epoch_hours(self.UTC_datetime, timezone="UTC")
	def GET_datetime_epoch_days(self):
		return GET_datetime_epoch_days(self.UTC_datetime, timezone="UTC")
		
	# ================================================================================================
	# LOCAL TIME CALULATIONS
	def GET_datetime_local_seconds(self, *args, **kwargs): #gives option to shoot in timezone as args or kwargs
		local_datetime = self.GET_datetime_local(timezone)
		return GET_datetime_localized_seconds(local_datetime, *args, **kwargs)
	def GET_datetime_local_minutes(self, *args, **kwargs):
		local_datetime = self.GET_datetime_local(*args, **kwargs)
		return GET_datetime_localized_minutes(local_datetime, *args, **kwargs)
	def GET_datetime_local_hours(self, *args, **kwargs):
		local_datetime = self.GET_datetime_local(*args, **kwargs)
		return GET_datetime_localized_hours(local_datetime, *args, **kwargs)
	def GET_datetime_local_days(self, *args, **kwargs):
		local_datetime = self.GET_datetime_local(*args, **kwargs)
		return GET_datetime_localized_days(local_datetime, *args, **kwargs)
		
	def GET_local_second_of_day(self, *args, **kwargs):
		local_datetime = self.GET_datetime_local(*args, **kwargs)
		return GET_localized_second_of_day(local_datetime, *args, **kwargs)
	def GET_local_minute_of_day(self, *args, **kwargs):
		local_datetime = self.GET_datetime_local(*args, **kwargs)
		return GET_localized_minute_of_day(local_datetime, *args, **kwargs)
	def GET_local_hour_of_day(self, *args, **kwargs):
		local_datetime = self.GET_datetime_local(*args, **kwargs)
		return GET_localized_hour_of_day(local_datetime, *args, **kwargs)

 

if __name__ == "__main__":
	# Test types
	print('Library makes DST assumption of local area, if not specified in Timestamp() creation, use kwarg "DST" to specify DST setting if desired')
	print('These tests are desined for window shop')
	
	print('\n=============================================')
	# Initialization-------------------------------------------------
	print("Testing Initialization:")
	
	# Now()
	stp = Timestamp()
	print("Now time in EST: ", stp.GET_datetime_local())
	stp = Timestamp(timezone="CMT")
	print("Now time in CMT: ", stp.GET_datetime_local())
	print('')
	
	# Datetime
	dtdt = datetime.now()
	stp = Timestamp(dtdt)
	print('Datetime now:             ', stp.GET_datetime_local())
	print('Datetime now, change_PST: ', stp.CHANGE_timezone("PST"))
	stp = Timestamp(dtdt, timezone="PST")
	print('Datetime now, force_PST:    ', stp.GET_datetime_local())
	print('')
	
	# Timedelta
	# about 29 years 
	total_days = 29*365
	total_timedelta = timedelta(days=total_days)
	stp = Timestamp(total_timedelta)
	print('Timedelta, about 29 years:          ', stp.GET_datetime_local())
	stp = Timestamp(total_timedelta, timezone="PST")
	print('Timedelta, about 29 years, set_PST: ', stp.GET_datetime_local())
	
	# Time tuples	
	stp = Timestamp(2020, 4, 23, 7, 37, 19, 999)
	print("Tuple, manual entry: ", stp.GET_datetime_local())
	
	# print('year, month, day')
	# print(Timestamp(2020, 4, 23,timezone="PST").GET_datetime_local())
	# print()
	stp = Timestamp(2020, 4, 23, 7, 37, 19, 999, timezone="PST")
	print("Tuple, manual PST  : ", stp.GET_datetime_local())
	
	time_tuple=(2020, 7, 2, 7, 37, 19)
	time_list=[2020, 4, 23, 7, 37, 19, 12351123]
	stp = Timestamp(time_tuple)
	print("Tuple, tuple entry   ", stp.GET_datetime_local())
	
	stp = Timestamp(time_list)
	print("Tuple, list entry:   ", stp.GET_datetime_local())
	
	print('\n=============================================')
	# time object transparency-------------------------------------------------
	print("Testing time object transparency using Now():")
	stp = Timestamp(timezone='EST')
	print("Raw Call: ", stp)
	print("Type: ,", type(stp))
	print("Type==Timestamp: ", type(stp)==Timestamp)
	print("Weekday : ", stp.weekday())
	print("Local_epoch_day: ", stp.local_epoch_day())
	print("UTC_epoch day  : ", stp.utc_epoch_day())
	print("Hour of day    : ", stp.local_hour())
	print("Minute of day  : ", stp.local_minute())
	print("Second of day  : ", stp.local_second())
	
	
	print("Weekday, PST : ", stp.weekday(timezone='PST'))
	print("Local_epoch_day, PST: ", stp.local_epoch_day(timezone='PST'))
	print("UTC_epoch day, PST  : ", stp.utc_epoch_day(timezone='PST'))
	print("Hour of day, PST    : ", stp.local_hour(timezone='PST'))
	print("Minute of day, PST  : ", stp.local_minute(timezone='PST'))
	print("Second of day, PST  : ", stp.local_second(timezone='PST'))
	
	print('\n=============================================')
	# Export/Import-------------------------------------------------
	print("Testing Import/Export:")
	str_export = stp._export()
	print("Export Dict: ", str_export)
	print("Attempting import...")
	tab = Timestamp._import(str_export)
	print("Succecssful import :", tab.local_hour())	
	
	# Removed Market clock specific functionality tests
	
	print('\n=============================================')
	# Adding timedelta-------------------------------------------------
	print("Testing timestamp addition with timedeltas:")
	print("Adding 30 minutes: ", Timestamp(timezone='EST') + timedelta(minutes=30))
	print("Adding 1 hour: ", Timestamp(timezone='EST') + timedelta(days=1))
	
	print('\n=============================================')
	# Subtracting-------------------------------------------------
	print("Testing timestamp subtraction methods:")
	print("Subtracting 30 minutes: ", Timestamp(timezone='EST') - timedelta(minutes=30))
	print("Subtracting 1 hour: ", Timestamp(timezone='EST') - timedelta(days=1))
	
	new_dt_time = datetime.now().time()
	print("DT_TIME subtraction: ",stp-new_dt_time)
	print("DT_TIME subtraction, type: ",type(stp-new_dt_time))
	
	print('\n=============================================')
	# UTC calculations-------------------------------------------------
	print("Testing UTC calculations:")
	print("UTC time: ", Timestamp(timezone='EST').GET_datetime_local('UTC'))
	
	print('\n=============================================')
	# localized calculations-------------------------------------------------
	print("Testing local timezone calculations:")
	print("Overload greater than: ",stp>new_dt_time )
	print("Overload less than: ",stp<new_dt_time )
	print("Overload equal too: ",stp==new_dt_time )