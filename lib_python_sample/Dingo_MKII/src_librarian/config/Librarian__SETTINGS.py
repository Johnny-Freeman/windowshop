''' Relative directory locations (Where/What you want to store your data files)
	-dir_parent
		-dir_EOD
		-Intraday Folders, by date
'''
from datetime import date

today = date.today()
str_today = str(today) + '/'

dir_parent = 'data_raw/'
dir_EOD = 'EOD/'
dir_zip = 'data_zip/'

CONFIG = {
	# Modes of operation corresponds to specific tag_filenames and directories
	'INTRADAY'	: {
					'dir_path'	: dir_parent + str_today,
					'zip_path'	: dir_zip + str_today,
					'extension'	: '.dat',	# file extension
					'separator'	: '\n',		# Data separator
				},
				
	'EOD'		: {
					'dir_path'	: dir_parent + dir_EOD + str_today,
					'zip_path'	: dir_zip + dir_EOD + str_today,
					'extension'	: '.dat',	# file extension
					'separator'	: '\n',		# Data separator
				},
}