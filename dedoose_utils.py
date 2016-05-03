# @author Jeff Lockhart <jwlock@umich.edu>
# utility functions for working with excerpts coded in dedoose and exported to flat files
# version 1.1

import pandas as pd
import re

'''Yes, ignoring warnings is bad, but the apply function in drop_uncoded
works reliably despite this warning (which only appears in some environments).
'''
pd.options.mode.chained_assignment = None

def col_merge(row, cols, fill_na=''):
    '''Sometimes Dedoose doesn't recognise that descriptor columns 
    from different imports are the same. This applyable function 
    merges them back together for us. 
    @cols : the list of columns to merge
    '''
    for c in cols:
        if pd.notnull(row[c]):
            #Each row will only have one school.
            #We can stop when we find it.
            return row[c]
    return fill_na

def clean_col_names(df):
    '''Dedoose column names are clumsy, like titling code applications 
    'Code: xxx Applied' and naming the start index of an excerpt 'Package'.
    Here's a function to simplify them.
    '''
    df = df.rename(columns=lambda x: re.sub('Code: ','',x))
    df = df.rename(columns=lambda x: re.sub(' Applied','',x))
    df = df.rename(columns=lambda x: re.sub('Package','Start',x))
    return df

def check_codes(row, cols):
    '''check whether this excerpt has the codes we care abotu applied to it.
    '''
    for c in cols:
        if row[c] == True:
            return True
    return False

def drop_uncoded(df, code_cols):
    '''Not all excerpts will have codes that we're interested in. This 
    function keeps just the ones that are relevant to our analysis.
    '''
    #Flag whether this excerpt has been coded with any of the codes we care about.
    df['xxcodedxx'] = df.apply(check_codes, cols=code_cols, axis=1)
    
    #Drop excerpts without any codes we care about
    df = df[df['xxcodedxx'] == True]
    
    #Drop our temporary column
    return df.drop('xxcodedxx', axis=1)
    
