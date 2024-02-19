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
import logging


def csv_reader(filename, caller):
    '''
    purpose:    use pandas to read in csv's.  
    input:      filename = filename to read in, caller=string (ldap or source) telling function which arguments read_csv should use
        csv input file must have a single header row with at least columns named 'Last' and 'First'
    output:     dataframe to pass back
    '''
    logging.info('%s CSV is about to be ingested', filename)
    try:
        if caller == 'ldap':
            dataframe = pd.read_csv(filename, index_col=None, header=None) # works for ldap
        elif caller == 'source':
            dataframe = pd.read_csv(filename) # works for census/terms
        else:
            logging.warning('When calling this function you must specify ldap or source, instead of %s', caller)
    except pd.errors.EmptyDataError:
        print('\n\n Empty data error - is the csv file empty?  The filename is specified in config.ldap_under_review \n\n')
        return
    except pd.errors.ParserError:
        print('\n\n Parser error - is the csv file missing rows? The filename is specified in config.ldap_under_review \n\n')
        return
    return(dataframe)   
    
def xlsx_reader(filename):
    '''
    purpose:    use pandas to read in excel files. 
    input:      filename to read in.  Excel file must:
        1. Have case-sensitive column headers 'Last Name' and 'First Name'
        2. Have no extra/empty rows before headers - which is usually the case with census/term provided by sox team
    output:     dataframe to pass back
    '''
    logging.info('%s EXCEL is about to be ingested', filename)
    
    try:
        dataframe = pd.read_excel(filename, index_col=None, header=0)
    except pd.errors.EmptyDataError:
        print('\n\n Empty data error - is the excel file empty?  The filename is specified in config.ldap_under_review \n\n')
        return
    except pd.errors.ParserError:
        print('\n\n Parser error - is the excel file missing rows? The filename is specified in config.ldap_under_review \n\n')
        return
    return(dataframe)
    
def ingest(sourcetype):
    '''
    purpose: read in csv or xlsx to dataframe and clean to prepare for comparison
    input:  type will be which datasource (terms, census, or users) and corresponds to a path in config.py
    output: is a dataframe passed back
    '''
    
    file_to_ingest = config.paths[config.env][sourcetype+"_path"]

    if file_to_ingest.endswith('.csv'):
        df = clean(csv_reader(file_to_ingest, 'source'))  
        
    elif file_to_ingest.endswith('xlsx'): 
        df = clean(xlsx_reader(file_to_ingest))
 
    else:
        logging.warning('%s will not work: file type must be either .csv or .xlsx', file_to_ingest)
        print('file type must be either .csv or .xlsx')

    # Make sure header has columns for First and Last, catch case where file is First Name or Last Name instead
    if {'First Name'}.issubset(df.columns):
         df.rename(columns={'First Name':'First'}, inplace=True)
    if {'Last Name'}.issubset(df.columns):
         df.rename(columns={'Last Name':'Last'}, inplace=True)    
    df['source']=sourcetype
    df['fullName']=df['First']+' '+df['Last']

    logging.info('%s now ingested with %s rows and ready to process', file_to_ingest, len(df.index))

    if type != 'users':   #terms and census (not users) sometimes have duplicates which throws off the matching
        df = df.drop_duplicates(subset = ['fullName'], keep='last')
    logging.info('%s Dataframe now has %s rows, after dropping duplicates', file_to_ingest, len(df.index))
    print('\n',sourcetype, '<-- dataframe starts with: \n', df[['First','Last','source']].head(),'\n\n','----------------'*2)
    
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
    df = csv_reader(file_to_ingest, 'ldap')

    try:
        userlist = df[0].values.tolist() 
    except Exception:
        print ("\n\n Hit an error turning the input file into a list, check that the userlist is populated \n\n")
        logging.error('Hit an error turning the input file into a list, check that the userlist is populated')
        return
    logging.info('About to perform an LDAP lookup against this userlist %s', list(userlist))
    #print("\n About to perform an LDAP lookup against this userlist: \n\n", list(userlist), "\n\n")
    
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
    logging.info('Begin matching lists')
    matched_dataframe = pd.merge(dataframe_to_test, dataframe_of_truth, how='outer')
    matches = matched_dataframe[matched_dataframe.duplicated(subset='fullName', keep='last')] # keeps only duplicates
    if matches.empty == False:
        matches.loc[:,'result'] = result_string
        print('\n\n\n these app users are on ',result_string,' list \n', matches)
        logging.info('Found matches on %s', result_string)
    else: 
        print('\n\n There were no ',result_string, '\n\n') #likely no term matches when input is ldap/ssulookups
        logging.info('There were no matches found on %s', result_string)
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
