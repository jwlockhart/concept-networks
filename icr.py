# @author Jeff Lockhart <jwlock@umich.edu>
# utility functions for inter-coder reliability
# version 0.2

import pandas as pd

def count_codes(coders, min_coders=1, max_coders=99999, 
                keep_coder_counts=False):
    '''Counts the number of coders who applied each code to each 
    excerpt.
    Input: 
        coders: a list of data frames with code applications
        keep_coder_counts: whether to keep the column counting number 
        of coders who coded an excerpt
    '''
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
    '''A simple merge of the codes from multiple coders.
    Input:
        coders: a list of data frames of code applications
        threshold: minimum number of coders applying a code for 
        us to use it. 
        unanimous: require all coders who coded an excerpt to 
        agree on a code before applying it
    '''
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
    '''Returns a DataFrame with counts for each column/code. Useful 
    for diagnostics.
    '''
    r = []
    for c in df.columns.values:
        tmp = df[c].value_counts().copy()
        tmp['code'] = c
        r.append( pd.DataFrame(tmp).transpose() )
    
    return pd.concat(r).fillna(0)

def percent_agreement(code_counts, n_coders):
    ''''''
    s = summarize(code_counts)
    n_rows = 1.0 * code_counts.shape[0]
    avg = 0.0
    r = pd.DataFrame()
    
    if n_coders == 2:
        r['percent_agree'] = 1 - (s[1] / n_rows)
        avg = r['percent_agree'].mean()
        
    elif n_coders < 2:
        print 'Must have at least 2 coders to compare.'
        return
    else:
        print '3+ coder percent agreement not yet implemented.'
        return
        
    return (r, avg)

def scotts_pi(code_counts):
    '''same as krippendorff's alpha in the limit and under certain conditions'''
    s = summarize(code_counts)
    pa, avg_pa = percent_agreement(code_counts, n_coders=2)

    #number of coded excerpts (x2 for 2 coders)
    n_obs = code_counts.shape[0] * 2.0
    
    #joint proportion squared for when each code is and is not applied
    #total number of 'true' cells over total cells
    pa['jp_true'] = ( (s[1] + (2 * s[2])) / n_obs ) ** 2
    #total 'false' cells over total cells
    pa['jp_false'] = ( (s[1] + (2 * s[0])) / n_obs ) ** 2
    #expected agreement
    pa['expected'] = pa['jp_true'] + pa['jp_false']
        
    pa['scotts_pi'] = ( ( pa['percent_agree'] - pa['expected'] ) 
                       / (1 - pa['expected']) )
    
    return (pa[['scotts_pi']], pa['scotts_pi'].mean())

def krippendorffs_alpha(code_counts):
    '''krippendorff's alpha in the case of: binary data, two coders, no missing values
    http://web.asc.upenn.edu/usr/krippendorff/mwebreliability5.pdf
    '''
    code_counts
    s = summarize(code_counts)
    n = code_counts.shape[0] * 2
    
    #obs disagree = cases where only 1 coder applied the code
    s['Do'] = s[1] 
    #row sum product = (actual neg + disagree) * (actual pos + disagree)
    s['rs'] = ( (s[0] * 2) + s[1] ) * ( (s[2] * 2) + s[1])
    
    s['krippendorffs_alpha'] = 1 - ((n - 1) * (s['Do'] / s['rs']))
    
    return (s[['krippendorffs_alpha']], s['krippendorffs_alpha'].mean())

def compute_icr(codes1, codes2):
    '''intercoder reliability for two coders with binary codes and no missing values'''
    counts = count_codes([codes1, codes2], min_coders=2)

    ka, avg = krippendorffs_alpha(counts)
    pi, avg = scotts_pi(counts)
    pa, avg = percent_agreement(counts, n_coders=2)

    return pd.concat([ka, pi, pa], axis=1).sort_values(by='krippendorffs_alpha')