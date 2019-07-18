import shutil

def ZIP_format_check(list_target, list_archive, format):
	if not len(list_target) == len(list_archive):
		raise ValueError("list_target must be same length as list_archive")
		
	if (not format == 'zip') and (not format == 'gzip'):
		raise ValueError("Formats must be zip or gzip")

def ZIP_files(list_target, list_archive, format):
	# Check
	if not type(list_target) == type([]):
		list_target = [list_target]
	
	if not type(list_archive) == type([]):
		list_archive = [list_archive]
		
	ZIP_format_check(list_target, list_archive, format)
	
	# Do
	print'Zipping Directories'
	for i in range(len(list_target)):
		print list_target[i]
		shutil.make_archive(list_archive[i], format, list_target[i])
		
		
"""
# https://stackoverflow.com/questions/27035296/python-how-to-gzip-a-large-text-file-without-memoryerror
# https://docs.python.org/2/library/tarfile.html

'tar.gz'
"""
import tarfile, os

def ZIP_largefiles(list_target, list_archive, format):
	# Check
	if not type(list_target) == type([]):
		list_target = [list_target]
	
	if not type(list_archive) == type([]):
		list_archive = [list_archive]
		
	# ZIP_format_check(list_target, list_archive, format)
	
	# Do
	print'Zipping Directories'
	for i in range(len(list_target)):
		print list_target[i]
		make_tarball(list_target[i], list_archive[i], format)

def make_tarball(source_dir, output_filename, format):
	output_filename += '.' + format
	tarball = tarfile.open(output_filename, "w:gz")
	
	tarball.add(source_dir, arcname=os.path.basename(source_dir))
	
	tarball.close()
	