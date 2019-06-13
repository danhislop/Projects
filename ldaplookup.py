#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Fri Jul  6 14:14:39 2018
@author: dan hislop
The purpose of this script: given a csv file of linux usernames, 
do an ldap lookup, then return a file with matching full names
If an LDAP lookup is not found, it is likely that account is either 
a utility account, or that person is no longer with company 

'''

import config
import util
import write_output
import ldap
import logging


def ldaplookup(names):
    '''
    input: a list of linux usernames, format:
        bwagner
        edherd
    goal: lookup each username against ldap and return the fullname, mailname, and email address
        this will make it easier to compare them to lists of terminated and active employees, 
        since those lists do not contain usernames, only full names
    output: a dict of username, cn, mailname 
    '''

    #initialize connection to LMI ldap server
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    con = ldap.initialize(config.ldap_server)
    
    # At this point, we're connected as an anonymous user, must use username/pwd from config file
    try:
        dn, local_pw =  util.parse_local_config(config.pwdfile)
    except FileNotFoundError:
        logging.error('Cannot find the local credentials file')

    logging.info('About to establish LDAP binding')    
    try: 
        con.simple_bind_s(dn,local_pw)
    except ldap.INVALID_CREDENTIALS as e:
        logging.error("There was a problem with the ldap.INVALID_CREDENTIALS:")
        logging.error(e)
        raise
    except ldap.SERVER_DOWN as e:
        logging.error("There was a problem connecting to LDAP: Double check the connectivity to the URL in config.py")
        logging.error(e)
        raise
    except:
        logging.error("Having trouble with LDAP")
        raise
    logging.info('LDAP binding established')


    #initialization complete

    lookupcount = 0
    findcount = 0
    errorcount = 0
    ldap_base = "ou=LogMeIn,dc=3amlabs,dc=net"
    namedict = {}
    namedict['username']= 'user','ldap_fullName','last', 'first', 'mailNickname', 'mail'


    for i in names:
        lookupcount +=1
        lookup = '(sAMAccountName='+i+')'
        try:
            result = con.search_s(ldap_base, ldap.SCOPE_SUBTREE, lookup, ['cn','mailNickname', 'mail'])
        except ldap.OPERATIONS_ERROR:
            logging.error('operations error, did ldap bind correctly?')


        try:
            r = (result[0])            
            try:
                full = (r[1]['cn'][0]).decode('utf-8')
                last = full.split()[1]
                first = full.split()[0]
            except:
                print("--- Couldn't split into last, first name  :", i)
                last, first = 'OneWordAccount', i
            namedict[i] = i, \
            (r[1]['cn'][0]).decode('utf-8'), \
            last, \
            first, \
            (r[1]['mailNickname'][0]).decode('utf-8'), \
            (r[1]['mail'][0]).decode('utf-8')  
            # after converting to python 3 required utf-8 decodes
            findcount +=1
        except:
            # Feedback: try to catch a specific error here, e.g. keyValueError
            print("The LDAP Lookup could not find the account:",i)
            namedict[i] = i, 'None Found','AccountNotFound', i, 'None',['None.Found']
            errorcount +=1
            
    print('\n Lookup complete.  Results: \n Searched ',str(lookupcount), 'names, \n Found: ', findcount, ' \n Could not find: ',str(errorcount))
    return namedict

def main():
    
    logging.info('Starting ldap lookup routine')
    
    # Create a python list of linux usernames from the ldap_under_review .csv listed in config.py 
    linux_usernames = util.input_ldapnames()
    
  
    # Do an LDAP lookup of the dataframe name by name, returning fullname, etc
    ldap_results_dict = ldaplookup(linux_usernames)
    
    
    # Convert the results list into a dataframe, label, and clean up
    ldap_results = util.process_ldap(ldap_results_dict)
    
    
    # Write the output to csv 
    write_output.write_csv(ldap_results)


if __name__ == "__main__":
    main()

