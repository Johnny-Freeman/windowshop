import os

Debug = False

class LibrarianSession(object):	
	"""
		1) Attempt to write to file based on Date + Source + DataType
		2) If not able, open instance of file in "a+" mode
	"""
	config_mode = None
	
	# Dictionary of files
	dir_path = None
	file_extension = None
	data_separator = None
	dict_file_instances = {}
	
	def __init__(self, config):
		self.dict_configs = config
		
	def SET_mode(self,mode):
		# First close all active files
		self.CLOSE_files()
		
		# reset file list
		self.dict_file_instances = {}
		
		try:
			self.config_mode = self.dict_configs[mode]
			self.file_extension = self.config_mode['extension']
			self.data_separator = self.config_mode['separator']
		except:
			print'Librarian: Mode not found!'
			pass
			
		self.CHECK_mode_directory()
			
	def CHECK_mode_directory(self):
		"""
			checks if directories are created,
				creates them if not
		"""
		self.dir_path = self.config_mode['dir_path']
		
		if not os.path.exists(self.dir_path):
			print'Making Directory: ', self.dir_path
			os.makedirs(self.dir_path)
		
	def __getitem__(self,key):
		return self.dict_file_instances[key]
		
	def CLOSE_files(self):
		for key in self.dict_file_instances:
			self.dict_file_instances[key].close()
	
	def WRITE_file(self, source, datatag, dataString):
		filename = source + '_' + datatag
		
		try:
			# Attempt to write to file as is assuming file is already open
			self.dict_file_instances[filename].write(dataString)
			self.dict_file_instances[filename].write(self.data_separator)
		except:
			# Assume file doesn't exist
			self.OPEN_file(filename)
			
			# Try again
			try:
				self.dict_file_instances[filename].write(dataString)
				self.dict_file_instances[filename].write(self.data_separator)
			except:
				print'ALERT: Unable to Write Data!'
	
	def OPEN_file(self, filename):
		full_filepath = self.dir_path + filename + self.file_extension
		self.dict_file_instances[filename] = open(full_filepath,'a+')
		
if Debug:
	import Librarian__SETTINGS, time
	manager = LibrarianSession(Librarian__SETTINGS.CONFIG)
	manager.SET_mode('INTRADAY')
	
	starttime = time.time()
	
	manager.WRITE_file('A','B','helloworld1')
	manager.WRITE_file('C','D','helloworld2')
	manager.WRITE_file('A','B','helloworld3')
	manager.CLOSE_files()
	raw_input(time.time()-starttime)