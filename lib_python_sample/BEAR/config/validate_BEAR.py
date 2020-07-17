# This is not actually needed yet, BEAR's primary purpose is to setup nonblocking sockets with poll(), along with message received at server end checking.

# def client_validate_response(input_bytes):
# 	input_string = input_bytes.decode('utf-8')
# 	
# 	_dict = {
# 		"valid"		= False,
# 		"payload"	= "debugging test",
# 	}
# 	return _dict
# 
# def server_validate_request(input_bytes):
# 	input_string = input_bytes.decode('utf-8')
# 	
# 	_dict = {
# 		"valid"			= True,
# 		"action"		= "debugging test",
# 		"parameters"	= "some dict parking lot",
# 	}
# 	return _dict