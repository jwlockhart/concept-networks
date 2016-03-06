# @author Jeff Lockhart <jwlock@umich.edu>
# utility functions for inter-coder reliability
# version 0.2

import pandas as pd

def count_codes(coders, overlap=False):
    """Counts the number of coders who applied each code to each 
    excerpt.
    Input: 
        coders: a list of identically shaped data frames (e.g. the 
        output of the alignment function)
        overlap: if True, only count excerpts all coders coded
    """
    result = coders[0].copy()
    
    if overlap:
        for i in range(1, len(coders)):
            result = result.add(coders[i])
    else:
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
    
    return pd.concat(r).fillna(0)