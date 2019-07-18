from threading import Thread
import time

Debug = False

def helper_callbackFunction(respholding_obj, i, function, args, kwargs):
	respholding_obj.responses[i] = function(*args, **kwargs)
	return

class CallBackHolder(object):
	def __init__(self, length):
		self.responses = [None for i in range(length)]
		
def Blocking_ThreadPool_wReturn(target, args_list=None, kwargs_list=None, que_delay=0, timeout=5):
	'''
		Takes a single function or list of functions, and passes them along to helper_callbackFunction along with location in response list
	'''
	# Input check
	# Either args_list or kwargs_list, needs to be populated to signify number of responses
	if args_list==None and kwargs_list==None:
		raise ValueError('Either args_list or kwargs_list needs to be populated to signify number of executions')
	
	elif (not args_list==None) and (not kwargs_list==None):
		try:
			length = len(args_list)
			if not len(kwargs_list)==length:
				raise
			if not type(args_list[0]) ==type([]):
				raise
			if not type(kwargs_list[0]) == type({}):
				raise
		except:
			raise ValueError('args_list and kwargs_list needs to be populated, of proper format, and same legnth if *using both args args and kwargs*')
	
	if kwargs_list==None:
		try:
			length = len(args_list)
			if not type(args_list[0]) ==type([]):
				raise
			kwargs_list= [ {} for i in range(length)]
		except:
			raise ValueError('Either args_list or kwargs_list needs to be populated, args_list=[[args],[args],]')

	if args_list==None:
		try:
			length = len(kwargs_list)
			if not type(kwargs_list[0]) == type({}):
				raise
			args_list=[ [] for i in range(length)]
		except:
			raise ValueError('Either args_list or kwargs_list needs to be populated, kwargs_list=[{kwargs},{kwargs},]')
	
	
	# if target = 1 function
	respholding_obj = CallBackHolder(length)
	thread_list = []
	
	if callable(target):
	
		# Start Threads
		for i in range(length):
			_t = Thread(target=helper_callbackFunction, args=[respholding_obj, i, target, args_list[i], kwargs_list[i]])
			thread_list.append(_t)
			thread_list[i].start()
			
			time.sleep(que_delay)
			
		# End Threads
		for i in range(length):
			thread_list[i].join(timeout)
	
	else:
		# More than one function, Length of args_list and kwargs_list must be the same
		if not len(target) == length:
			raise ValueError('Legnth of function list and args_list, kwargs_list must be same if using paired functions and arguments')
	
		# Start Threads
		for i in range(length):
			_t = Thread(target=helper_callbackFunction, args=[respholding_obj, i, target[i], args_list[i], kwargs_list[i]])
			thread_list.append(_t)
			thread_list[i].start()
			
			time.sleep(que_delay)
			
		# End Threads
		for i in range(length):
			thread_list[i].join(timeout)
	
	
	# return LIST of thread responses
	return respholding_obj.responses

# *************************************************************************************
def funct_sq(i):
	return i*i
	
def funct_tri(i):
	return i*i*i
	
def main():
	response = Blocking_ThreadPool_wReturn([funct_sq, funct_tri, funct_sq], args_list=[[1],[2],[3]])
	print response

if __name__ == '__main__':
	if Debug:
		main()