#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 13:56:10 2019

@author: dan hislop |  https://github.com/danhislop | hislopdan@gmail.com
Purpose: supports compare.py
"""
import config
import pandas as pd
import configparser

def csv_reader(filename):
    '''
    purpose:    use pandas to read in csv's.  but putting in own function, exceptions can be spelled out
    input:      filename to read in
    output:     dataframe to pass back
    '''
    
    try:
        dataframe = pd.read_csv(filename, index_col=None, header=None)
    except pd.errors.EmptyDataError:
        print('\n\n Empty data error - is the csv file empty?  The file is specified in config.ldap_under_review \n\n')
        return
    except pd.errors.ParserError:
        print('\n\n Parser error - is the csv file missing rows? The file is specified in config.ldap_under_review \n\n')
        return
    return(dataframe)   

    
def ingest(sourcetype):
    '''
    purpose: iterate through a datasource by reading in csv and cleaning to prepare for comparison
    input:  type will be which datasource (terms, census, or users) and corresponds to a path in config.py
    output: is a dataframe passed back
    '''
    
    file_to_ingest = config.paths[config.env][sourcetype+"_path"]
    df = clean(pd.read_csv(file_to_ingest))
    df['source']=sourcetype
    df['fullName']=df['First']+' '+df['Last']
    print('\n **** loaded csv file for ',sourcetype, ', with ', len(df.index), ' rows')
    if type != 'users':   #terms and census (not users) sometimes have duplicates which throws off the matching
        df = df.drop_duplicates(subset = ['fullName'], keep='last')
    print('**** after dropping duplicates, this dataframe now has ', len(df.index))
    print('\n  list starts with: \n', df.head(9),'\n\n','------------------------'*3)
    
    return(df)
    
    

def input_ldapnames(): 
    '''
    purpose: convert csv list of usernames into python list
    input: a csv file with list of usernames to look up, one per line 
    example input is
        username1
        usernname2
    output: a list of strings called userlist
    '''    
    userlist=[]
    file_to_ingest = config.paths[config.env]["ldapusers_path"]
    df = csv_reader(file_to_ingest)

    # feedback: try/except possibilities
    try:
        userlist = df[0].values.tolist() 
    except Exception:
        print ("\n\n Hit an error turning the input file into a list, check that the userlist is populated \n\n")
        return
    print("\n About to perform an LDAP lookup against this userlist: \n\n", list(userlist), "\n\n")
    
    return(userlist)
    
    
    
def clean(dirty_dataframe):
    '''
    purpose = clean up so only lowercase alphanumeric characters remain
        this will make it more accurate to compare two lists
    input = dataframe of names in format last,first
    output = dataframe of cleaned names
    '''

    # turns each column into lower case strings, and concatenates all columns (since str only works for series)
    lower = pd.concat([dirty_dataframe[col].astype(str).str.lower() for col in dirty_dataframe.columns], axis=1)
    #removes non-alpha characters including spaces
    clean_dataframe = pd.concat([lower[col].astype(str).str.replace('\W','') for col in lower.columns], axis=1)
        # update column case
    clean_dataframe.columns = clean_dataframe.columns.str.title()
    
    return(clean_dataframe)
    
    
    
def matchlists(dataframe_to_test,dataframe_of_truth,result_string):
    '''
    purpose: given two dataframes of people, create a third of their matches
    input: two dataframes to be matched
    output: new df of names which are in both dataframes
    '''
    
    matched_dataframe = pd.merge(dataframe_to_test, dataframe_of_truth, how='outer')
    matches = matched_dataframe[matched_dataframe.duplicated(subset='fullName', keep='last')] # keeps only duplicates
    if matches.empty == False:
        matches.loc[:,'result'] = result_string
        print('\n\n\n these app users are on ',result_string,' list \n', matches)
    else: 
        print('\n\n There were no ',result_string, '\n\n') #likely no term matches when input is ldap/ssulookups
    
    return(matches)
    
    
    
def find_lastname_matches(dataframe_to_test,dataframe_of_truth, label):
    '''
    purpose: find cases where fullname doesn't match, but last name does, to give hints for unclear cases
    input: two dataframes to be lastname-matched
    output: new df of lastname matches, with column labelling source of those names (term or census)
    '''
    lastname_matches = pd.merge(dataframe_to_test,dataframe_of_truth, on=['Last'], how='inner')
    lastname_matches.rename(columns={'fullName_x':'users_to_audit', 'fullName_y':label}, inplace=True)
    return lastname_matches



def parse_local_config(file_name):
    '''
    purpose: read credentials from configuration file
    input: a file with plaintext password (security hole that should be closed)
    example file looks like:
        [my_account]
        username = 3amlabs\my_username
        password = my_password
    output: username, password from separate file
    '''
    config = configparser.ConfigParser()
    config.read_file(open(file_name))
    p = config.get("my_account","password")
    dn = config.get("my_account","username")
    
    return(dn, p)


def process_ldap(ldap_results_dict):
    '''
    purpose: process, label, and drop unneeded column
    input: a dict of linux usernames
    output: a dataframe of username, cn, mailname, etc
    '''
    
    ldap_results = pd.DataFrame.from_dict(ldap_results_dict).transpose()
    ldap_results.rename(columns={0: 'user', 1: 'ldap_fullName', 2: 'last', 3: 'first', 4: 'mailNickname', 5: 'mail'}, inplace=True)
    ldap_results.drop(ldap_results.head(1).index, inplace=True)  # this removes first row which was a duplicate of header
    
    return(ldap_results)
