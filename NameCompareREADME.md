# Purpose: to assist with comparing lists of users with lists of current employees 
This project was initiated for SOX compliance.


## Structure: 
* **ldaplookup.py:** Takes a .csv of unix usernames and does an LDAP lookup against company directory, returning Full Names from otherwise cryptic usernames. 
* **namecompare.py:** Compares .csv lists of Full Names against a good list ("census") and bad list ("terminations"). Categorize clear matches, and point out ambiguous ones. 
* **util.py:** Utility Functions as described 
* **write_output.py:** All functions for writing to xlsx and csv 
* **config.py:** Settings related to input files, output files, environments
* **ldapcred.txt:** (in some cases):  if doing LDAP lookups, save your credentials into a text file using example provided, ldapcred_example.txt.  This is a security risk slated for improvement.

# What you'll need: 
The primary use is to compare names between the app under audit.  here, audit means determine which users are still with the company (in census) or not (in term list).
* Your Files
	* Start with a csv file of Last, First names pulled from the app. If no export, names can even be scraped from admin website as with Tableau.
	* If your names are "full names" then for now, you must first separate into separate .csv columns as last, first. 
* Environment
	* Tested with python3 environment
    * install these dependencies:  pandas, ldaplookup, ldap, configparser, xlsx_writer
    * create a subdirectory called "data"

# How to setup for Last, First name matching: 
* Place your csv files in ./data/ folder 
* Specify names of these files in config.py 
* If your input is ldap/linux usernames instead of Last, First, see below section. otherwise, set run_namecompare_against_ldap_results = 'no'

# How to setup for LDAP/Linux usernames:
Some apps only provide usernames, making it hard to match against full names showing on the census. Hive/Datalake usernames is one example. 
*  Place your .csv of usernames in ./data/ folder. The .csv will only have one column, "usernames" 
*  In config.py, set this filename as 'ldap_under_review'. 
*  Set run_namecompare_against_ldap_results = 'yes' 
*  Confirm the ldap server address listed in config.py is accurate. 
*  Use the file 'ldapcred_example.txt' as a template to input your username/password, then save the file as ldapcred.txt in same folder as the .py files.

# How to Execute: Execute namecompare.py 
* Output will be an xlsx file in ./data/ folder.
* The 'clear cases' tab are audited and matched, either against census or terms.
* Now look through the 'unclear cases' for partial matches to help you manually find matches. 
* Often these will be cases like "Jim Smith" vs. "James Smith".
