#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  7 10:28:47 2019
@author: dan hislop 

Purpose: formats and writes dataframe into an xlsx file 
"""

import config
import pandas as pd

writer = pd.ExcelWriter(config.paths[config.env]['namecompare_output'])

def excel_sheet(dataframe, label, column_names):
    ''' purpose: create excel sheet in output file given:
        inputs:
            dataframe = the data to write into the tab
            label = give the excel tab (sheet) a name
            column_names = list of column titles for this tab
        output: excel sheets ready to write - requires excel_workbook function to produce output
    '''
    dataframe.to_excel(writer, label, index=True, columns=column_names)
    
    
def excel_workbook():
    ''' 
    purpose: finalizes the excel worksheet with formatting, writing, and saving the file. 
    input: none
    output: xlsx file saved to path specified in config
    '''
    #       some excel formatting to help
    workbook = writer.book
    worksheet = writer.sheets["hints for unclear cases"]
    worksheet1 = writer.sheets["clear cases"]
    worksheet.set_zoom(120)
    red_format = workbook.add_format({'bg_color':'#FFC7CE','font_color': '#9C0006'})
    green_format = workbook.add_format({'bg_color':'#C6EFCE','font_color': '#006100'})
    worksheet1.conditional_format('F1:F300', {'type':'cell','criteria': 'equal to','value':'"matched_term_list"','format':red_format}) 
    worksheet1.conditional_format('F1:F300', {'type':'cell','criteria': 'equal to','value':'"matched_census"','format':green_format})        
    for i in writer.sheets.values():
        i.set_column(1,5,20)
        
    writer.save()



def write_csv(data_to_write):   
    '''
    purpose: write ldap output to csv
    input: a dataframe of names
    output: a csv file containing user, fullname, last, first, mailnickname, mail
    '''  
    
    data_to_write.to_csv(config.paths[config.env]["ldap_output"])
    print("\n\n CSV file written to : ",config.paths[config.env]["ldap_output"])   
    