# Introduction to R_boxplots, R-python integration
First project in R, sorts through set of 16000 microRNA sequencing dataset and present concentrated boxplots in shared dataplots.
	* This data has been gathered as part of an ongoing research project in conjunction with the University of Cincinnati College of Medicine, as such - Context and original individual Sample_IDs in dataset have been removed. Demos will be scheduled on an individual basis.

makeboxplot - R_script
	Original script developed to manually sort through dataset, and produce boxplots containing specific genesets.
	
makeboxplot_py - R-Python integration
	Same script as makeboxplot, but parameterized to be ran in conjunction with python script
	
pythonworld - Python script
	Python script used to automate production of boxplots

merged_allgene_alltissue - Parsed Dataset
	Original Raw Dataset has been excluded from GIT. Example of neatly organized dataframes produced through python/Rscript. Original headers removed to exclude context and individual and number of samples.
	
dataplots - Candy
	Graphs of resultant boxplots from dataset. Titles/sample_size/significance removed.