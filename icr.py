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
    cols = coders[0].columns.values
    
    for i in range(1, len(coders)):
        for c in cols:
            result[c] = result[c] + coders[i][c]
    
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

