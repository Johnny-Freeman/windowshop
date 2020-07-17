from pytz import timezone, utc

LOCAL_TIMEZONE = "EST"
LOCAL_DAYLIGHT_OVERRIDE = None # True/False, None (recommended, lets algo dictate when daylightsavings is)

# compile and most used timezones
# https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568
timezones = {
	"PST"	:	timezone("US/Pacific"),
	"CMT"	:	timezone("US/Central"),
	"EST"	:	timezone("US/Eastern"),
	"GMT"	:	timezone("Europe/London"),
	"JST"	:	timezone("Japan"),
	"HKT"	:	timezone("Hongkong"),
	"CST"	:	timezone("Asia/Shanghai"),
	"IST"	:	timezone("Asia/Kolkata"),
	"UTC"	:	utc,
}

def GET_TIMEZONE(str_zone):
	try:
		return timezone(str_zone)
	except:
		raise ValueError("Timezone not found in pytz module, please see official pytz list")