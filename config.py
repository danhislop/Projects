#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 13:56:10 2019

@author: dan hislop |  https://github.com/danhislop | hislopdan@gmail.com
Purpose: supports compare.py
"""

'''
config files for sox compliance tools: namecompare.py and ldaplookup.py
terms and census stay constant for each search, 
app_under_review can be updated based on which app is being reviewed
'''

# ---------- SET THIS SECTION FOR EACH RUN (START) --------------------------------------
# Specify input files to be reviewed.  ldap is not always used.
# IMPORTANT: set run_name_compare_against_ldap_results to yes in order to first do ldaplookup, then run namecompare on its output

ldap_under_review = 'piishort'
app_under_review = 'Tableau2019'
run_namecompare_against_ldap_results = 'yes'

if run_namecompare_against_ldap_results == 'yes':
    app_under_review = ldap_under_review + '_ldap_output'

# ---------- SET THIS SECTION FOR EACH RUN (END) --------------------------------------
    

# LDAP Server information
ldap_server = 'ldaps://10.1.1.21'
pwdfile = 'ldapcred.txt'

# Environment:  prod will be used except for testing with pre-defined test files
env = 'prod'     #use larger prod dataset
#env = 'test'    #use small test dataset



paths = {
        'prod': {
            'terms_path' : './data/terms2019.csv',
            'census_path' : './data/census2019.csv',
            'users_path' : './data/' + app_under_review + '.csv',
            'ldapusers_path' : './data/' + ldap_under_review + '_ldap.csv',
            'ldap_output' : './data/' + ldap_under_review + '_ldap_output.csv',
            'namecompare_output' : './data/namecompare_output_' + app_under_review + '.xlsx'},
        'test': {
            'terms_path' : './data/terms_test.csv',
            'census_path' : './data/census_test.csv',
            'users_path' : './data/users_test.csv',
            'ldapusers_path' : './data/ldapusers_test.csv',
            'ldap_output' : './data/ldapusers_ldap_output.csv',
            'namecompare_output' : './data/namecompare_test_output.xlsx'}
}

