"""
	Stand alone utility to compress and make archive
"""

target_input = ["2018-07-23"]
compression_format = "tar.gz"

# *************************************************************************************
from make_Archive_utils.Zip_files import ZIP_largefiles

ZIP_largefiles(target_input, target_input, compression_format)
