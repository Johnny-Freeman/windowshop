"""
	Sets communication protocol for transmitting data to client
	
	datagram = <time_requested> <time_received> <array_error_found> <array_data>
	
	msg_delimiters = <time_requested> |text_delimiter| <time_received> |text_delimiter| <array_error_found> |text_delimiter| <array_rawString_data> |delimiter|
	
	|delimiter|			= represents the entire object of data, or a new line of data
	|text_delimiter|	= represents intra data limiters to setup the datagram on the receiving end, without the need to parse on the spot (parsing is then handled through mutli process on the client side)
	
	currently coded as:
	Client should make request as <GET/POST method> |space| <stream request tag>
"""

CONFIG_SERVER1 = {
	'address'		: 'localhost',
	'port'			: 8094,
	'buffer'		: 4096,
	'num_sockets'	: 8,
	
	# Communication Protocol
	'timeout_socket': 0.2,		# Maximum time the server should wait for message from client
	'delimiter'		: r'\\',	# regular expression to match, this is just a newline, simple enough and rare for jsons to have
	'text_delimiter': r'&&',	# a sub delimiter to separate out pieces of individual, can be more than one character since the initial delimiter handles the entire data message
	
	# Allowed Server Tags
	'allowedMethods': ['GET','POST'],
	'allowedStreams': ['Stock_Chart_Minute_Candle','Option_Chart','Stock_Tick_Second','Stock_Chart_Minute_Average'],
}

CONFIG_SERVER2 = {
	'address'		: '192.168.1.51',
	'port'			: 8095,
	'buffer'		: 4096,
	'num_sockets'	: 7,
	
	'delimiter'		: r'\\', # regular expression to match, this is just a newline, simple enough and rare for jsons to have
}