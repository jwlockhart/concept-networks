# encoding=utf8

# @author Jeff Lockhart <jwlock@umich.edu>
# utility functions for inter-coder reliability
# version 1.0

import pandas as pd
from sklearn.metrics import cohen_kappa_score
import sys
sys.path.insert(0,'outside_code/')
import krippendorff_alpha as ka

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
            result[c] = (counts[c] == counts['xxx_n_coders_xxx'])
    
    else:
        for c in counts.columns.values:
            #we have enough coders, but do enough of them 
            #agree on this code?
            result[c] = (counts[c] >= threshold)
    
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
    '''Returns the simple percent agreement statistic for two coders'''
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
    '''Scott's Pi statistic. Assumes two coders, no missing data.
    Scott, W. A. (1955). Reliability of Content Analysis: The Case of Nominal Coding. Public Opinion Quarterly, 19(3), 321–325
    '''

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

def cohens_kappa(codes1, codes2):
    '''Cohen's Kappa statistic. Assumes 2 coders, no missing data.
    Cohen, J. (1960). A Coefficient of Agreement for Nominal Scales. Educational and Psychological Measurement, XX(1), 37–46.
    '''
    r = []
    code_counts = count_codes([codes1, codes2], min_coders=2, keep_coder_counts=True)
    s = summarize(code_counts)
    s['cohens_kappa'] = 0
    
    code_cols = codes1.columns.values
    
    x = codes1.copy()
    y = codes2.copy()
    x['n_coders'] = code_counts['xxx_n_coders_xxx']
    y['n_coders'] = code_counts['xxx_n_coders_xxx']
    x = x[x['n_coders'] == 2]
    y = y[y['n_coders'] == 2]
    
    for c in code_cols:
        k = cohen_kappa_score(x[c].values, y[c].values)
        s.ix[c, 'cohens_kappa'] = k
        
    return (s[['cohens_kappa']], s['cohens_kappa'].mean())

def compute_icr(codes1, codes2):
    '''Returns several measures of intercoder reliability for two coders 
    with binary codes and no missing values.
    '''
    counts = count_codes([codes1, codes2], min_coders=2)

    ka, avg = krippendorffs_alpha(counts)
    pi, avg = scotts_pi(counts)
    pa, avg = percent_agreement(counts, n_coders=2)
    ck, avg = cohens_kappa(codes1, codes2)
    
    #merge our metrics into a single dataframe
    together = pd.concat([ka, pi, ck,pa], axis=1).sort_values(by='krippendorffs_alpha')
    
    #add a column for the number of excerpts matching each code at least once
    together['n'] = 0
    for c in counts.columns.values:
        together.ix[c, 'n'] = counts[counts[c] > 0].shape[0]
        
    return together.drop('xxx_n_coders_xxx')

def get_k_alpha(coders, col_name):
    '''Wrapper for external krippendorff function. Works with 
    multiple coders and missing data.'''
    tmp = []
    for c in coders:
        tmp.append(c[col_name].to_dict())
        
    return ka.krippendorff_alpha(data = tmp, 
                                 metric = ka.nominal_metric)

def get_n(row, counts):
    c = row['code']
    return counts[counts[c] > 0].shape[0]

def compute_multi_icr(coders):
    '''ICR for multiple coders and missing values. 
    Returns a data frame with Krippendorffs alpha and
    the number of items used to calculate it (i.e. 
    those coded by more than one coder).'''
    
    #find alphas
    result = []
    cols = coders[0].columns.values
    i = 0
    for col in cols:
        tmp = {}
        tmp['code'] = col
        tmp['alpha'] = get_k_alpha(coders, col)
        result.append(tmp)
        i += 1
        print 'Finished', i, 'of', len(cols)
        
    #Save alphas in dataframe
    r = pd.DataFrame.from_records(result)
    
    #find coder counts for each item
    cs = icr.count_codes(coders, min_coders=2)
    
    #store n items with each code
    r['n'] = r.apply(get_n, counts=cs, axis=1)
    
    return r.sort_values(by='alpha', ascending=False)




















