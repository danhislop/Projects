#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 10:28:47 2019
@author: dan hislop 

Purpose: takes input from CSV files of Last, First names and looks for matches
         This was designed for SOX audits, to check a list of application users against
         a list of current employees (census) and terminated employees (terms)
"""
import config
import util
import ldaplookup
import pandas as pd
import write_output

pd.options.mode.chained_assignment = None 


def main():

    # Set name of .csv file to ingest in config.py
    
    # Ingest the files, returning dataframes to compare with each other
    terms = util.ingest('terms')
    census = util.ingest('census')
    users = util.ingest('users')
    
    
    # create matchlists for census and terms
    users_match_census = util.matchlists(users, census, 'matched_census')
    users_match_terms = util.matchlists(users, terms, 'matched_terms')
    
    
    # combine clear cases into one list:  these are direct matches on census or on term list 
    clear_cases = pd.merge(users_match_census, users_match_terms, how = 'outer') # should be no duplicates already
    clear_cases = clear_cases.sort_values(by=['result','First'], ascending=[False,True])
    
    
    # now find those that haven't matched either list.  These should be human reviewed.
    users_clear = pd.merge(users,clear_cases, how='outer')
    unclear_cases = users_clear[~users_clear['result'].isin(['matched_census', 'matched_terms'])]
    
    
    # When fullnames aren't matched, finding a Last Name match might help 
    maybe_terms = util.find_lastname_matches(unclear_cases, terms, 'fullName_on_termlist')
    maybe_census = util.find_lastname_matches(unclear_cases, census, 'fullName_on_census')
    maybes = pd.concat([maybe_terms, maybe_census], sort=True)
    
    
    print("\n\n       The remaining users are unclear.  \n \
          Maybe this will help: these last names match either census or termlist: \n \
          Check for nicknames like Chris for Christopher \n",)
    print(maybes[['users_to_audit','fullName_on_census','fullName_on_termlist','source_y']])
    
    #--------create output--------------------------
    
    # Column Names for different purposes
    output_columns = ["Last","First","source","fullName"]
    result_columns = ["Last","First","source","fullName", "result"]
    maybe_columns= ['users_to_audit','fullName_on_census','fullName_on_termlist','source_y']
                    
    
    # Write Results
    write_output.excel_sheet(clear_cases, "clear cases", result_columns)
    write_output.excel_sheet(unclear_cases, "unclear cases", result_columns)
    write_output.excel_sheet(maybes, "hints for unclear cases", maybe_columns)
    
    
    # Write Reference files (the input files, formatted)
    write_output.excel_sheet(census, "quarterly census list", output_columns)
    write_output.excel_sheet(terms, "quarterly term list", output_columns)
    write_output.excel_sheet(users, "app under inspection", output_columns)
    
    
    # Write everything into a workbook and save
    write_output.excel_workbook()


# Determine whether to first run ldaplookup. if so, then its output will be used for namecompare in main()
if config.run_namecompare_against_ldap_results == 'yes':
    ldaplookup.main()
    print("\n Triggering ldaplookup first \n")
    

if __name__ == "__main__":
    main()






