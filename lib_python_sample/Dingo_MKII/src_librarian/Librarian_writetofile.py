'''
	Primary Purpose is to write data to file
	
	Also handles zipping up data and uploading to main server for backup
'''
from config import Librarian__SETTINGS
from config import NodeServer__SETTINGS
from utils.Zip_files import ZIP_largefiles
from utils import Transfer_files
from utils.FileSessionManager import LibrarianSession

Debug = False

# ****Globals**********************************************
_librarian = LibrarianSession(Librarian__SETTINGS.CONFIG)


def init(mode=None):
	_librarian.SET_mode(mode)
	
	print'Librarian says Helloworld\n'
	
def shutdown():
	_librarian.CLOSE_files()
	
	print'Librarian shutdown\n'

def SORT_Write_Datagram(datagram):
	'''
		Sort the datagram and use specific function to write file
	'''
	_librarian.WRITE_file(	datagram.source, datagram.tag,	# These Parameters define the filename
							str(datagram.localtime_requested) + '\t' + str(datagram.localtime_received) + '\t' + str(datagram.error) + '\t' + str(datagram.rawData)	)
							
def ZIP_TRANSFER_files():
	"""
		1) Zip files
		2) Transfer Files to server
		3) Delete unzipped files
	"""
	_librarian.CLOSE_files()
	
	format = 'tar.gz'
	
	# Zip files
	list_targets = []
	list_archives = []
	list_zipfiles = []
	
	for key in Librarian__SETTINGS.CONFIG:
		list_targets.append(	Librarian__SETTINGS.CONFIG[key]['dir_path'][:-1]	)
		list_archives.append(	Librarian__SETTINGS.CONFIG[key]['zip_path'][:-1]	)
		list_zipfiles.append(	Librarian__SETTINGS.CONFIG[key]['zip_path'][:-1] + '.'+format	)
		
	ZIP_largefiles(list_targets, list_archives, format)
	
	# Transfer Files
	Transfer_files.TRANSFER_files(NodeServer__SETTINGS.CONFIG_NODE2, list_zipfiles)
	
	# Delete RawData, keep zip
	for file in list_targets:
		Transfer_files.DeleteLocalFiles(file,'DIRECTORY')
	
	print'Zip and Transfer completed'

# MAIN FUNCTION TO CALL**********************************
def Slave_WriteProcess(PipeIN, PipeOUT, *args, **kwargs):
	'''
		This is the Function to call in it's own process
		Does only a few state things.
	'''	
	_run = True
	
	while(_run):
		message = PipeIN.recv()
		
		if Debug:
			print'Librarian msg received: ', message
		
		if message['command'] =='SHUTDOWN':
			shutdown()
			_run = False
			break
			
		elif message['command'] =='INITIATE':
			init(**message['payload'])
			response = {
					'command':'INITIATED'
				}
			PipeOUT.send(response)
			
		elif message['command'] =='MODE':
			init(message['payload'])
			
		elif message['command'] =='DATAGRAM':
			SORT_Write_Datagram(message['payload'])
			
		elif message['command'] =='ZIP' or message['command'] =='TRANSFER':
			ZIP_TRANSFER_files()
			response = {
					'command':'TRANSFER'
				}
			PipeOUT.send(response)

if Debug:
	import time
		
	str_10million = ''
	for i in range(10000000):
		str_10million +='1'
	
	data = [str_10million]
	
	starttime = time.time()
	x = str(data)
	file = open('test.dat','a+')
	file.write(x+x+x)
	file.close()
	
	print time.time()-starttime