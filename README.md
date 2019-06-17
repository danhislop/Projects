# NameCompare matches lists of names against each other. 
### When input file contains linux usernames (instead of full names), an LDAP lookup will return fullnames for comparison.

---

## Why use NameCompare?
#### This project was initiated for SOX compliance. During compliance week, we are given:
* Census list ('census') with Last, First names of all current employees
* Termination list ('terms') with Last, First names of all recently terminated employees
* We use the admin interface of any application to generate our own list of employees enabled to use that app ('users').  

#### Our goal: determine if each name on the app user list is on the census (good) or term (bad) list.
####
#### Name Compare's output is an excel file to assist your audit, with several tabs:
| Output Tab | Contents |
|------------|----------|
|`Clear Cases` | Means a match was found, showing either 'matched_terms' or 'matched_census'|
|`Unclear Cases` | Means no match was found |
|`Hints for Unclear Cases` | Suggests partial matches that can be used by a human to make a determination. (Often these will be cases like "Jim Smith" vs. "James Smith")|
|`Remaining 3 tabs` | Simply record a view of the census, terms, and users that were used in Name Compare.|



---
# What you'll need: 
The primary use is to compare names between the app under audit.  here, audit means determine which users are still with the company (in census) or not (in term list).
* Input Files
	* User list under audit - from your application
		* csv file of Last, First names pulled from the app. If no export is avaialble, names can be scraped from admin website and cleaned up into the .csv.
		* If your names are "full names" then you must first separate into separate .csv columns as last, first (future improvement). See excel formula hint below
	* Census File and Terminations File.  Can be either .csv or .xlsx:
		* EXCEL -Easiest: .xlsx file provided by compliance group: TOP ROW MUST BE COLUMN HEADERS, key column names are "First Name" and "Last Name". 
			You probably need to remove a few blank lines before input.  
		* CSV: should contain two simple columns "Last" and "First" separated by commas
			Last,First
			Jordan,Michael
			
* Environment
	* Tested with python3 environment
    	* install these dependencies:  pandas, ldaplookup, ldap, configparser, xlsx_writer
    	* create a subdirectory called "data" for outputs.  Put your input files here as well.

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

---
## File Structure: 
* **ldaplookup.py:** Takes a .csv of unix usernames and does an LDAP lookup against company directory, returning Full Names from otherwise cryptic usernames. 
* **namecompare.py:** Compares .csv or .xlsx lists of Full Names against a good list ("census") and bad list ("terminations"). Categorize clear matches, and point out ambiguous ones. 
* **util.py:** Utility Functions as described 
* **write_output.py:** All functions for writing to xlsx and csv 
* **config.py:** Settings related to input files, output files, environments
* **ldapcred.txt:** (in some cases):  if doing LDAP lookups, save your credentials into a text file using example provided, ldapcred_example.txt.  This is a security risk slated for improvement.

--
## Excel Tip 
* Given a list of Full Names in excel, the following formulas will exctract First, Last name to create separate columns: 

| Full Name | First Name | Last Name |
|------------|----------|----------|
|'Alex Morgan' in cell A2|=LEFT(A2,FIND(" ",A2,1)-1) |=RIGHT(A2,LEN(A2)-FIND(" ",A2,1))|
|Alex Morgan|Alex|Morgan|