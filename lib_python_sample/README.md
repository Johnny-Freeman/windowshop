Async Database Connections

	Library to handle FAST async postgresql database connections.
	
	Primarily used for queries and large datasets where scans are not optimal, otherwise use ORMs. (Async is a feature NOT handled by ORMs!)
	Due to async nature, library allows multiple queries to be ran in realtime, simutaneously. Only drawback is SQL knowledge requirement.
	
	For results see results_images in containning folder.

BEAR

	Demonstrates low level socket ability. Written and deployed in REST-like envronments to allow async network requests between data applications. 

FRAMEWORK - "framework"

	General user library wrote to experiment with tread/process handling. Written for Python 2.7.
	
	FRAMEWORK is depreciated and is intented to display 27 capabilities. Techniques are depreciated.

DINGO - Dingo_MKII

	Old unsupported project version, originally meant to query per-second Financial data from various REST-api sources. Configurations/passwords deleted so will not work as is.
	This functioned as such: Query REST-api for JSON > parse JSON into tables > write tables to 29GB files > compress files to 3GB for storage. 
	
	Showcases understanding of REST, python thread/process management, object orientated.
	
NeuralNet_Bayesian_Classes - Machine Learning Library
	
	Newer addition to Dingo_financial_data. Sets up full mathematical and neural net framework for pattern recognition. Training methods have intentionally been left out.
	
	Showcases understanding of discrete Bayesian statistics.
	
WORLD CLOCK

	Extensive clock library built on top of built-in datetime and pytz. Properly takes timepoint in any timezone and maps to any other timezone, with proper handling of DST.
	
	Deployed by Apsistech payroll [portal](http://admin.apsistech.com:5000/) and market data wrangler.