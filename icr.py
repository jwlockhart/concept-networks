# @author Jeff Lockhart <jwlock@umich.edu>
# utility functions for inter-coder reliability
# version 0.2

import pandas as pd

def count_codes(coders, min_coders=1, max_coders=99999, 
                keep_coder_counts=False):
    """Counts the number of coders who applied each code to each 
    excerpt.
    Input: 
        coders: a list of data frames with code applications
        keep_coder_counts: whether to keep the column counting number 
        of coders who coded an excerpt
    """
    result = coders[0].copy()
    result['xxx_n_coders_xxx'] = 1
    
    for i in range(1, len(coders)):
        tmp = coders[i]
        tmp['xxx_n_coders_xxx'] = 1
        result = result.add(tmp, fill_value=0)
    
    #select only the rows where we have the right number of coders
    result = result[(result['xxx_n_coders_xxx'] >= min_coders) & 
                    (result['xxx_n_coders_xxx'] <= max_coders)]
    
    if not keep_coder_counts:
        result = result.drop('xxx_n_coders_xxx', axis=1)
    
    return result

def simple_merge(coders, threshold=1, unanimous=False, 
                 keep_coder_counts=False):
    """A simple merge of the codes from multiple coders.
    Input:
        coders: a list of data frames of code applications
        threshold: minimum number of coders applying a code for 
        us to use it. 
        unanimous: require all coders who coded an excerpt to 
        agree on a code before applying it
    """
    counts = count_codes(coders, min_coders=threshold, 
                         keep_coder_counts=True)
    result = pd.DataFrame()
    
    if unanimous:
        for c in counts.columns.values:
            #we selected n_coders > threshold already
            result[c] = counts[c] == counts['xxx_n_coders_xxx']
    
    else:
        for c in counts.columns.values:
            #we have enough coders, but do enough of them 
            #agree on this code?
            result[c] = counts[c] >= threshold
    
    if not keep_coder_counts:
        result = result.drop('xxx_n_coders_xxx', axis=1)
    
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