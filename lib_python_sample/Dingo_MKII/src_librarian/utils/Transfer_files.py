'''
	After the End of Day data finishes and zipped up, Transfer  files to server
'''

import urllib2, shutil
from smb.SMBHandler import SMBHandler

def TRANSFER_files(SMBconfig, list_files):
	
	print'Starting Transfer to Server'
	
	# Write Values to server location
	server_path = 'smb://' + \
	SMBconfig['username'] + ':' + SMBconfig['password'] + '@' + \
	SMBconfig['address'] + SMBconfig['dir_path']
	
	# Transfer Intra day zip target
	for path in list_files:
		TransferFiles2Server(	full_local_filename	= path,
								server_target_path	= server_path)


def TransferFiles2Server(full_local_filename, server_target_path):
	
	filehandler = open(full_local_filename,'rb')

	director = urllib2.build_opener(SMBHandler)
	
	fh = director.open(server_target_path + full_local_filename, data = filehandler)
	
	fh.close()
	
def DeleteLocalFiles(target, mode='FILE'):
	'''
		Currently will just delete the current Day's Files after they have been uploaded to server if script crashes, the data will still be local!
	'''
	if mode == 'DIR' or mode == 'DIRECTORY':
		#remove entire directory
		shutil.rmtree(target)
	else:
		#remove single file
		os.remove(target)
	return
