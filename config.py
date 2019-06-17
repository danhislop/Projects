#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 13:56:10 2019

@author: dan hislop |  https://github.com/danhislop | hislopdan@gmail.com
Purpose: supports compare.py
"""

'''
config files for sox compliance tools: namecompare.py and ldaplookup.py
terms and census stay constant for each search
app_under_review can be updated based on which app is being reviewed
'''



# ---------- SET THIS SECTION EACH NEW APP UNDER REVIEW  --------------------------------------

# ldap is used when input is linux usernames (set run_name_compare_against_ldap_results='yes') rather than full names (run_name_compare_against_ldap_results = 'no'). 
# Setting to 'yes' will first do ldaplookup, then run namecompare on its output

# INPUT FILENAMES FOR APP USER NAMES - must be .csv, leave off extension.  e.g. ldap_under_review = 'mycsvfile_with_no_extension'
ldap_under_review = ''
app_under_review = 'USWNT_to_audit'
#app_under_review = 'tableauQ22019'
run_namecompare_against_ldap_results = 'no'



# ---------- SET BELOW SECTION ONCE EACH QUARTER  --------------------------------------

# LDAP Server information, must be reachable from your host (in office or via vpn)
ldap_server = 'ldaps://10.1.1.21'
pwdfile = 'ldapcred.txt'  # make sure to set your username and password into this file

# Environment:  use prod unless testing with pre-defined test files
env = 'test'    #use small test dataset
#env = 'prod'     #use larger prod dataset


# DO NOT CHANGE THIS LINE:
if run_namecompare_against_ldap_results == 'yes':
    app_under_review = ldap_under_review + '_ldap_output'

# THE PATHS BELOW REFER TO INPUT (AND SOME OUTPUT) FILENAMES 
# TERMS AND CENSUS FILES CAN BE .XLSX, BUT MUST:
    # 1. Have case-sensitive column headers 'Last Name', 'First Name'
    # 2. Have no extra/empty rows before headers - which is usually the case with census/term provided by sox team
# If TERM/CENSUS are .csv then expecting column headers 'Last' and 'First'

paths = {
        'prod': {
            #'terms_path' : './data/terms2019.csv',    # sourcefile can be .csv or .xlsx
            #'census_path' : './data/census2019.csv',  # sourcefile can be .csv or .xlsx
            'terms_path' : './data/Termination Report.xlsx',
            'census_path' : './data/Employee Census.xlsx',
            'users_path' : './data/' + app_under_review + '.csv',  # must be .csv
            'ldapusers_path' : './data/' + ldap_under_review + '.csv',
            'ldap_output' : './data/' + ldap_under_review + '_ldap_output.csv',
            'namecompare_output' : './data/namecompare_output_' + app_under_review + '.xlsx'},
        'test': {
            'terms_path' : './testdata/USWNT.PriorPlayers.xlsx',
            'census_path' : './testdata/USWNT.CurrentRoster.xlsx',
            'users_path' : './testdata/' + app_under_review + '.csv',
            'ldapusers_path' : './testdata/ldapusers_test.csv',
            'ldap_output' : './testdata/ldapusers_ldap_output.csv',
            'namecompare_output' : './testdata/namecompare_output_' + app_under_review + '.xlsx'}
}

