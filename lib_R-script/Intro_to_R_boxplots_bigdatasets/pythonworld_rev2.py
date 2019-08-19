"""
	Automate the boxplot making process
	Objective:
		- Learn how to interface rscript with python
		- loopthrough options and generate a bunch of separate boxplots
	
	To do list:
	1) get args input to work in rscript
	2) have Rscript write out pdf based on names specified here
"""
import subprocess

#config
path2_R = "F:/R/R-3.6.1/bin/Rscript.exe" #F:\R\R-3.6.1 << input full directory path to R-executeable
path2_Script = "E:/R_script/REMOVED/makeboxplot_py_rev3.R" # <<input full directory path to  R_script #E:\R_script\REMOVED

list_REMOVED_1 = ["MT1E","MT1F","MT2A","MT1X","GSTO1","GLRX","AKR1C3","POR","IL11","CXCL14","CISH","FHIT","VPS18","HIST1H4C"]
list_REMOVED_2 = ["SLC22A7", "SLC34A1", "SLC13A1", "SLC6A20", "SLC38A4", "SLC3A2"]
list_REMOVED_3 = ["FA2H", "CYB5R1", "ELOVL7", "CYP27A1", "DHRS11", "DHCR7", "ALDH3B1", "CHPT1", "PMVK", "AGPAT2", "FABP1"]
list_REMOVED_4 = ["AKR1C8P", "AKR1B10"]
list_REMOVED_5 = ["SLC1A2", "GRIK3", "GRM8", "KCNK2", "GABRD", "LGR5", "ATP2B2", "TRPC1", "PTHLH", "GAS6", "C1QTNF4", "DLL4"]
list_REMOVED_6 = ["GDF6", "ADAMTS18", "ADAM33", "BOC", "PCDHGB6", "ST8SIA6", "PRIMA1", "VASH1", "PODN", "RHOJ", "PROX1", "HOXD9"]
list_REMOVED_7 = ["SOX18", "TFAP2E", "ID3", "ASCL2", "EBF2", "HSF4", "EBF3", "SCARA3", "IGF2", "ADCY5", "RGL3", "TM6SF1"]

list_dict_genes_to_display = {
	"list_REMOVED_2": list_REMOVED_2,
	"list_REMOVED_3": list_REMOVED_3,
	"list_REMOVED_4": list_REMOVED_4,
	"list_REMOVED_1": list_REMOVED_1,
	"list_REMOVED_5": list_REMOVED_5,
	"list_REMOVED_6": list_REMOVED_6,
	"list_REMOVED_7": list_REMOVED_7,
}

#script args
input_file = "E:/R_script/REMOVED/csv_input/merged_allgene_alltissue_allsmoke-nonsmoke.csv" # <<Input full directory path to

class cmd_Rscript():
	def __init__(self):
		self.output = None
	
	# Recussion flating a list of strings
	def flatten_str_list(self, args):
		if type(args) == type("str"):
			return [args]
		else:
			flatargs = []
			for el in args:
				flatargs += self.flatten_str_list(el)
			return flatargs

	def RUN_cmd(self, args):
		cmd = [path2_R, path2_Script] + args
		flat_cmd = self.flatten_str_list(cmd)
		print "Running cmd: " + str(flat_cmd)
		self.output = subprocess.check_output(flat_cmd, universal_newlines=True)
		print "rScript successfully ran with args: " + str(args)
		print "\n"
		
	def GET_output(self):
		return self.output

def RUN_script(r_script_subprocess, commands):
	r_script_subprocess.RUN_cmd(commands)
	print r_script_subprocess.GET_output()

def main():
	process_bank = []
	
	count=0
	for key in list_dict_genes_to_display:
		r_script = cmd_Rscript()
		process_bank.append(r_script)
		
		outfilename = str(key)+str(count)+".pdf"
		commands = [input_file, outfilename, list_dict_genes_to_display[key] ]
		RUN_script(r_script, commands)
		
		count+=1
	
	raw_input()

main()