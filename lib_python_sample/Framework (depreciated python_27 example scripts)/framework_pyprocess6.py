'''
	Due to lack of process management
	, try to write a process manager
	
	Method_A displayed here requires process timing, but works surprisingly well!!
'''
from multiprocessing import Pipe, Process, Queue
from threading import Thread # Unfortunately, one function requires use of a thread, search ##Thread to see
import time

def f_proc_shell(funct, queue, pipeOUT, proc_delay):
	'''
		State function which commands process to do something and return result back to pipe
	'''
	while(True):
		try:
			# Grab Queue
			comm = queue.get(block = False)
			# Shutdown is handled by terminate() in _main_
			
			# Execute command
			respObj = funct(*comm['args'])
			
			# Form response
			fullresp = {}
			fullresp['n_order'] = comm['n_order']
			fullresp['respObj'] = respObj
			
			# Return Response
			pipeOUT.send(fullresp)

		except:
			time.sleep(proc_delay)
			pass

def run_Proc_wDelay(funct=None, arg_list=[], que_delay=0, Processes=4, proc_delay=0.02):
	'''
		Remember it takes a LIST of arg_Sets (plural) = list[    set1[arg1,arg2,arg_i]      , set2[arg1,arg2,arg_i]             ]

		These non-class functions currently lack timeout ability and will loop forever if child process never returns
		Use the CLASS process manager if you believe your child process will be unstable
	'''
	# Handles
	n = len(arg_list)
	list_proc = []
	list_pipe = []
	list_resp = [None for i in range(n)]
	
	# Que, shared by all
	queue = Queue()
	
	
	# Setup Slave Processes
	for i in range(Processes):
		pipeIN, pipeOUT = Pipe()
		p = Process(target=f_proc_shell, args=[funct, queue, pipeOUT, proc_delay])
		
		list_proc.append(p)
		list_pipe.append(pipeIN)
		
		p.start()
	
	
	# Loop indefinitely while waiting for processes to finish
	j = 0
	while(True):
		# Check if anything in pipes
		# Collect response if so
		for pipe in list_pipe:
			if pipe.poll():
				respdict = pipe.recv()
				n_order = respdict['n_order']
				list_resp[n_order] = respdict['respObj']

		# Check if list_resp has been filled, break loop once filled
		try:
			list_resp.index(None)
		except:
			break
		
		# Send Command to process
		if j < n:
			# create command
			comm={}
			comm['args'] = arg_list[j]
			comm['n_order'] = j
			
			# send command
			queue.put(comm)
			if j < n-1:
				# Only wait if not last one
				time.sleep(que_delay)
				# INSERT OTHER FUNCTIONS YOU WANT TO EXECUTE IN MAIN THREAD HERE
			
			j+=1

	# Shutdown processes
	for p in list_proc:
		# terminate maybe windows specific
		p.terminate()
		p.join()
	
	return list_resp

class FunctionOrderState(object):
	'''
		Object to hold functions and corresponding commands
		Also tracks status of FunctionOrder, and progress through process execution and number of retries sent back through
	'''
	def __init__(self,
				funct = None,
				args = None,
				n_order = 0,
				n_retry = 0):
		
		self.funct = funct
		self.args = args
		self.n_order = n_order
		self.n_retry = n_retry
		
		# Holds Response object if any, when function is executed
		self.respObj = None
		

def f_proc_shell_wManager(queue, pipeOUT, proc_delay, PID):
	'''
		State function which commands process to do something and return result back to pipe
	'''
	while(True):
		try:
			# Grab Queue
			comm = queue.get(block = True)
			# Shutdown is handled by terminate() in _main_
			
			# Decode function - ALSO, the fact the line executes indicates queue successfully grabbed
			funct = comm.funct
			
			# Increment n_retry
			comm.n_retry +=1
			
			# Timeout solution: Pass PID back through PIPE to initiate handshake with main thread
			# Indicates process has started to execute task and to begin watchdog/timeout count
			pipeOUT.send(('OPEN', PID, comm))
			
			# Execute command
			comm.respObj = funct(*comm.args)
			
			# Return Response
			pipeOUT.send(('DONE', PID, comm))

		except:
			if proc_delay > 0.0:
				# Ever so small overhead
				time.sleep(proc_delay)
			pass

def HelperFunct_resubmit_TimedOut_process(comm, queue, que_delay, n_que_order=1):
	time.sleep(que_delay * n_que_order)
	queue.put(comm)
	return
	
class ProcessSyncManager(object):
	'''
		Starts up slave processes that waits for functions and arg_list
		Takes arg_list and returns results list in the SAME ORDER! 
	'''
	def __init__(	self,
					Processes = 4,
					que_delay = 0,
					proc_delay = 0,
					proc_timeout = 5,
					proc_retry = 0):
		
		# init variables
		self.Processes = Processes
		self.proc_delay = proc_delay
		self.proc_timeout = proc_timeout
		self.proc_retry = proc_retry
		self.que_delay = que_delay
		self.list_proc = []
		self.list_pipe = []
		self.proc_watchdog = []
		self.queue = Queue()
		self.ON = None
		
		# init / load functions
		self.load_processes()
		
		# Response List
		self.list_resp = []
		
	def terminate_restart_process(self, PID):
		''' AKA Process REPAIR
			Forcefully terminate and restart child process
			This is part of solution to prevent code timeouts
		'''
		# Terminate Process, and pipe (pretty certain you terminate the processes first before terminating the pipe)
		self.list_proc[PID].terminate()
		self.list_proc[PID].join()
		self.list_pipe[PID] = None
		
		# Create a new pipe and process
		pipeIN, pipeOUT = Pipe()
		p = Process(target=f_proc_shell_wManager, args=[self.queue, pipeOUT, self.proc_delay, PID])
		
		# Install pipe and process into manager list
		self.list_proc[PID] = p
		self.list_pipe[PID] = pipeIN
		
		# Start process
		self.list_proc[PID].start()
		print'Process timeout and "repaired" (PID): ',PID
		
		return
		
	def load_processes(self):
		'''
			loads processes into list, really should be hidden from user
			, unless they want to restart manager
			
			edit: process can only be used once and not restarted, here we fake it by just refreshing
		'''
		self.list_proc = []
		self.list_pipe = []
		for i in range(self.Processes):
			pipeIN, pipeOUT = Pipe()
			p = Process(target=f_proc_shell_wManager, args=[self.queue, pipeOUT, self.proc_delay, i])
			
			self.list_proc.append(p)
			self.list_pipe.append(pipeIN)
		
		self.proc_watchdog = [ False for i in range(self.Processes)]
	
	def handle_commResponse(self,comm):
		'''
			Handles the return objects from executing process functions
			In blocking mode (displayed here), it updates list_resp to reflect outcome
			In non-blocking mode (defined later), it will append to growing list of responses, and splice list to match buffer size
		'''
		n_order = comm.n_order
		self.list_resp[n_order] = comm.respObj
	
	def handle_progress(self):
		'''
			Once commands have been sent to individual processes
			This function is looped to check up on Status of Command_Order
			Grabs response if available
		'''
		# Check if anything in pipes
		# Collect response if so
		for pipe in self.list_pipe:
			if pipe.poll():
				'''
					Now dealing with timeouts, pipe now passes back p_resp = [<'OPEN'or'DONE'; State>, PID, response dictionary], see below
					
					Pipe return object changes based on process state:
					Process starting: ['OPEN', PID, comm]
					Process Finished: ['DONE', PID, comm]
				'''
				
				''' #combined into one line
				#resp_dict = pipe.recv()
				p_resp = pipe.recv()
				
				# Extract response information
				State = p_resp[0]
				PID = p_resp[1]
				comm = p_resp[2]
				'''
				# Extract response information
				State, PID, comm = pipe.recv()
				
				
				if State == 'DONE':
					# Process completed Successfully
					# Reset proc_watchdog
					self.proc_watchdog[PID] = False
					
					# n_order represents response order
					self.handle_commResponse(comm)
				
				else:
					# Process has started, update proc_watchdog 
					# n_order = comm.n_order
					
					# process start_time, store comm_orderstate in case it times out
					self.proc_watchdog[PID] = [time.time(), comm]		
	
	def check_processWatchdog_handleTimeouts(self, que_delay = None):
		'''
			Does Two things
			1) Checks if an actively working process has timeout
				Will restart process if timeout
			2) Resubmits Command_order to queue if number of retries allows for it
		'''
		current_sec = time.time()
		j_delay = 1
		for PID in range(self.Processes):
			
			# If process active
			if not self.proc_watchdog[PID] == False:					
				# Calculate elapsed time since process start
				d_sec = current_sec - self.proc_watchdog[PID][0]
				
				if d_sec > self.proc_timeout:
					# If process times out, reset process
					self.terminate_restart_process(PID)
					
					comm = self.proc_watchdog[PID][1]
					# Check if able to retry command_order
					
					if comm.n_retry > self.proc_retry:
						# number of retries passed
						# Return time out result
						comm.respObj = {'Error':'Process TIMEOUT, nth_index = ' + str(comm.n_order)}
						self.handle_commResponse(comm)
					
					else:
						# Otherwise retry command order
						
						if que_delay==None:
							# use default
							que_delay = self.que_delay
						
						# Threads are nasty, this is a low risk thread to use
						t_resubmit = Thread(target=HelperFunct_resubmit_TimedOut_process, args=[comm, self.queue, que_delay, j_delay]) ##Thread
						t_resubmit.start()
						
						# Delay submission of next comm_order by additional time
						j_delay+=1
					
					# Reset watchdog for PID
					self.proc_watchdog[PID] = False
	
	def do_process(self, funct, arg_list, que_delay=None):
		'''
			Blocking until all results returned
			Remember it takes a LIST of arg_Sets (plural) = list[    set1[arg1,arg2,arg_i]      , set2[arg1,arg2,arg_i]             ]
		'''
		# Check if processes are active
		active = False
		for p in self.list_proc:
			active = (active or p.is_alive())
		if not active:
			print'None of the process are not active, please turn on using obj.start_processes()'
		
		n = len(arg_list)
		self.list_resp = [None for i in range(n)]
		
		# Loop indefinitely while waiting for processes to finish
		'''
			Indefinite loop turning out to cause problems on WWW, will hang if HTTP drops signal! Use timeouts!
				or retries(will likely result in exceeding limits, but at least it wont hang the program! (missing one or two pieces of information per minute)
				
				a timeout will need to be programmed in, since these deadlocked threads will eventually build up over a day and hog CPU power
				Turns out to be a complex problem:
				1)* We need to embule each process with it's PID at creation
				2)* Send back the PID down the pipe to indicate which processID is responsible for which task
				3) Keep track of each pipeOUT end for potential timeout
				4)* If timeout found, call process terminate and restart function
		'''
		j = 0
		while(True):
			# Check if anything in pipes, and status of individual processes and grabs response if available
			self.handle_progress()
			
			# Check proc_watchdog for timeout
			self.check_processWatchdog_handleTimeouts(que_delay)
	
			# Check if list_resp has been filled, break loop once filled
			try:
				self.list_resp.index(None)
			except:
				break

			# Send Command to process
			if j < n:
				# create command
				'''
				comm={}
				comm['funct'] = funct
				comm['args'] = arg_list[j]
				comm['n_order'] = j
				'''
				comm = FunctionOrderState(funct = funct,
										args = arg_list[j],
										n_order = j)
				
				# send command
				self.queue.put(comm)
				if j < n-1:
					# Only wait if not last one
					if que_delay==None:
						# use predefined que_delay
						time.sleep(self.que_delay)
					else:
						#use new que delay
						time.sleep(que_delay)
					
					# INSERT OTHER FUNCTIONS YOU WANT TO EXECUTE IN MAIN/PARENT THREAD HERE
				
				j+=1
			
		return self.list_resp
		

	def start_processes(self):
		
		# If newly loaded manager
		if self.ON ==None:
			for p in self.list_proc:
				p.start()
			self.ON = True

		# If previously ran processes, reload processes then start again
		elif self.ON == False:
			self.load_processes()
			for p in self.list_proc:
				p.start()

			self.ON = True
	
	def stop_processes(self):
		if self.ON == True:
			for p in self.list_proc:
				# terminate maybe windows specific
				p.terminate()
				p.join()

			self.ON = False
			
def NonBlockingProcessManager_Function(args, kwargs, pipeIN, proc_delay = 0.02):
	'''
		Ran in process to unblock main thread
		Used by NonBlockingProcessManager, this also doubles as example code if you need to access the ResponseBuffer = NonBlockingProcessHandler.getResponseBuffer()
		
		Currently the NonBlockingProcessManager does not support .getResponseBuffer()
	'''

	NBPH = NonBlockingProcessHandler(*args, **kwargs)
	
	NBPH.start_processes()
	
	if 'proc_delay' in kwargs:
		proc_delay = kwargs['proc_delay']

	while(True):
		if pipeIN.poll():
			
			object = pipeIN.recv()
			
			if type(object)==type('str'):
				if object=='SHUTDOWN':
					break
			
			NBPH.do_process(*object)
			
			# check process timeout
		else:
			NBPH.handle_progress()
			NBPH.check_processWatchdog_handleTimeouts()
			time.sleep(proc_delay)
	return True

class NonBlockingProcessManager(object):
	def __init__(self, *args, **kwargs):
		'''
			automates the NonBlockingProcessHandler setup
			pipeINPUT is used to pass do_process(self, funct, arg_list, que_delay=None) objects into non blocking handler
			
			Example Usage:
			NBPM = NonBlockingProcessManager(**kwargs) (see ProcessSyncManager() for **kwargs)
			NBPM.STARTUP()
			# Do as many times as needed
			NBPM.do_process(funct, arg_list, que_delay)
			
			# When finished Shutdown
			NBPM.SHUTDOWN()
		'''
		self.pipeINPUT, self.pipeOUT = Pipe()
		
		# self.NBPH = NonBlockingProcessHandler(*args, **kwargs)
		self.args = args
		self.kwargs = kwargs
		
		# Only loaded in start_processes
		self.process_Loop = None
	
	def do_process(self, funct, arg_list, que_delay=None):
		try:
			test = arg_list[0][0]
		except:
			print'Warning arg_list needs to be formatted [ [arg,b] , [c,d] , [etc] ]'
			print'Assuming arg_list is in form [arg,b]; converting to [ [arg,b] ]'
			arg_list=[arg_list]
			pass
		self.pipeINPUT.send((funct, arg_list, que_delay))
	
	def STARTUP(self):
		# AssertionError: can only start a process object created by current process
		# very unfortunate, but p.start() must occur with-in process which created it, meaning self.NBPH = NonBlockingProcessHandler(*args, **kwargs) needs to be created in process_Loop

		self.process_Loop = Process(target = NonBlockingProcessManager_Function, args=[self.args, self.kwargs, self.pipeOUT])
		self.process_Loop.start()
		
	def SHUTDOWN(self):
		self.pipeOUT.send('SHUTDOWN')
		self.process_Loop.terminate()
		self.process_Loop.join()
		
			
class NonBlockingProcessHandler(ProcessSyncManager):
	'''
		Example usage:
			deF non Blocking handling function:
				NBPH = NonBlockingProcessHandler(**kwargs)
				NBPH.start_proc
				
				LOOP:
					if pipe.poll():
						object = pipe.recv()
						
						if object =='Shutdown'
							break
						
						NBPH.pipe.do_process(object)
					
					# check process timeout
					else:
						NBPH.handle_progress
						NBPH.check_processWatchdog_handleTimeouts()
			
			PipeINPUT, pipeOUT = Pipe()
			process = Process(target = non Blocking handling function, args=[**kwargs, pipeOUT])
			process. start
			
			PipeINPUT.send(object)
	'''
	def __init__(self, ResponseBuffer = 16, *args, **kwargs):
		ProcessSyncManager.__init__(self,*args, **kwargs)

		self.Blocking = False 
		self.NonBlocking = not self.Blocking
		self.ResponseBuffer = ResponseBuffer
		
		self.list_resp = []
		
	def handle_commResponse(self,comm):
		'''
			Handles the return objects from executing process functions
			In blocking mode (displayed here), it updates list_resp to reflect outcome
			In non-blocking mode (defined later), it will append to growing list of responses, and splice list to match buffer size
		'''
		n_order = comm.n_order
		self.list_resp.append(comm.respObj)
		self.list_resp = self.list_resp[-self.ResponseBuffer:]
	
	def getResponseBuffer(self):
		list = self.list_resp
		#resets list
		self.list_resp = []
		return list
	
	def do_process(self, funct, arg_list, que_delay=None):
		''' Modified to be Non Blocking
			Similar in function to the blocking version where order mattered, this one just feed the existing pool of processes and returns immediately
			It is up to the programmer to feed pipes into <funct, args> for return values
			
			The main benefit of this class over using the default pool is this class has built in timeout and retry handler
		'''
		
		# Check if processes are active
		active = False
		for p in self.list_proc:
			active = (active or p.is_alive())
		if not active:
			print'None of the process are active, please turn on using obj.start_processes()'
		
		n = len(arg_list)
		
		''' Not tracking responses in the non sync version
		list_resp = [None for i in range(n)]
		'''
		
		# Send Command to process
		for j in range(n):
			# create command
			'''
			comm={}
			comm['funct'] = funct
			comm['args'] = arg_list[j]
			comm['n_order'] = j
			'''
			comm = FunctionOrderState(funct = funct,
									args = arg_list[j],
									n_order = j)
			
			# send command
			self.queue.put(comm)
			if j < n-1:
				# Only wait if not last one
				if que_delay==None:
					# use predefined que_delay
					time.sleep(self.que_delay)
				else:
					#use new que delay
					time.sleep(que_delay)
				
				# INSERT OTHER FUNCTIONS YOU WANT TO EXECUTE IN MAIN/PARENT THREAD HERE
				
			
		return True	# list_resp