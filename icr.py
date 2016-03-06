# @author Jeff Lockhart <jwlock@umich.edu>
# utility functions for inter-coder reliability
# version 0.1


import pandas as pd

def count_codes(coders):
    """counts the number of coders who applied each code to each 
    excerpt.
    Input: 
        coders: a list of identically shaped data frames (e.g. the 
        output of the alignment function)
    """
    result = coders[0].copy()
    
    for i in range(1, len(coders)):
        result = result.add(coders[i], fill_value=0)
    
    return result

def simple_merge(coders, threshold=1):
    """A simple merge of the codes from multiple coders.
    Input:
        coders: a list of identically shaped data frames (e.g. the 
        output of the alignment function)
        threshold: minimum number of coders applying a code for 
        us to use it. 
    """
    counts = count_codes(coders)
    
    result = pd.DataFrame()
    for c in counts.columns.values:
        result[c] = counts[c] >= threshold
    
    return result

def summarize(df):
    """Returns a DataFrame with counts for each column/code. Useful 
    for diagnostics.
    """
    r = []
    for c in df.columns.values:
        tmp = df[c].value_counts().copy()
        tmp['code'] = c
        r.append( pd.DataFrame(tmp).transpose() )
    
    return pd.concat(r)