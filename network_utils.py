# @author Jeff Lockhart <jwlock@umich.edu>
# utility functions for making network graphs out of code/tag applications in qualitative data
# version 0.1

import pandas as pd
import networkx as nx
from math import sqrt

def make_net(data, min_weight=0, isolates=False, directed=False):
    '''Create a networkx network from our dataframe of edge weights
    Input:
        data: a symmetric pandas data frame of edge weights
        min_weight: ignore weights at or below this number
        isolates: boolean, do we include nodes without edges?
    '''
    nodes = data.columns.values
    
    if directed:
        g = nx.DiGraph()
    else:
        g = nx.Graph()
        #this case will have us add all edges twice, but nx doesn't mind
        #and a graph of codes is too small for the performance to matter
    
    #if we want to include even nodes without edges
    if isolates:
        g.add_nodes_from(nodes)
            
    #iterate over data matrix
    for r in nodes: #rows
        for c in nodes: #columns
            if r == c:
                #skip self-loops
                continue
            #if this edge has enough weight, add it
            if data.ix[r, c] > min_weight: 
                g.add_edge(r, c, weight = data.ix[r, c])                      

    return g

def var(x,n):
    '''variance for proportion'''
    return abs(x*(1-x))/n

def sdiv(x,n):
    '''standard deviation for proportion'''
    return sqrt(var(x,n))

def get_freq(data):
    '''Compute the frequencies of each code/column
    '''
    rows = 1.0 * data.shape[0] #number of rows as float
    cols = data.columns.values
    stats = pd.DataFrame()
    
    stats['count'] = data.sum()
    stats['frequency'] = data.mean()  
    stats['var'] = data.var()
    
    return stats

def rand_cooccur(data, stats):
    '''Compute the probability of any two codes cooccurring, assuming 
    the codes are independent.
    '''
    cols = data.columns.values
    rand_co = stats.copy()
    
    #create columns for each code as the probability of cooccurance
    #with the code in each row, assuming independence
    for c in cols:
        rand_co[c] = rand_co['frequency'] * stats.ix[c, 'frequency']
    
    #drop vestigial columns from stats df
    return rand_co.drop(['count', 'frequency', 'var'], axis=1)
    
def real_cooccur(data, stats):
    '''Compute how often we observe codes together in the real data.
    '''
    cols = data.columns.values
    real_co = stats.copy()
    rows = 1.0 * data.shape[0] #rows as float
    
    for r in cols: #rows
        for c in cols: #columns
            #set this cell to the fraction of rows with both codes
            real_co.ix[r, c] = data[(data[r]) & 
                                  (data[c])].shape[0] / rows
    
    #drop vestigial columns from stats df
    return real_co.drop(['count', 'frequency', 'var'], axis=1)

def normed_diff(rand, real, stats):
    '''Compute the normalized difference between the observed
    cooccurrance rates and those expected under the assumption of
    independence for undirected graphs. 
    '''
    #use our predicted cooccurrance matrix as a template
    cols = rand.columns.values
    z = rand.copy()

    for r in cols: #rows
        for c in cols: #columns
            #difference between actual and predicted values
            diff = (real.ix[r, c] - rand.ix[r, c]) 
            #standard deviation under null hypothesis
            stdiv = sqrt((stats.ix[r, 'var']) + 
                                   (stats.ix[c, 'var']))
            #TODO: fix this stdiv 
            #z-scores 
            z.ix[r, c] = diff / stdiv
    
    return z 

def directed_random(data, stats):
    '''Calculate the conditional probability of seeing each code given
    that we've seen each other code, assuming codes are independent.
    '''
    cols = data.columns.values
    dr = stats.copy()  
    
    for r in cols: #rows
        for c in cols: #columns
            #we expect to see c in instances of r at the same
            #rate we see c overall
            dr.ix[r, c] = stats.ix[c, 'frequency']
    
    return dr.drop(['count', 'frequency', 'var'], axis=1)

def directed_proportions(data, stats):
    '''Calculate the real rate at which we see each code given
    that we have seen each other code. I.e. calcuate the condifence
    of each rule A -> B for all pairs of codes A, B.
    '''
    cols = data.columns.values
    dp = stats.copy()

    for r in cols: #rows
        for c in cols: #columns
            #count of r as float
            alone = 1.0 * stats.ix[r, 'count']
            if alone == 0:
                #avoid div/zero error for codes we never see
                dp.ix[r, c] = 0
            else:
                #count of r and c together
                together = data[(data[r]) & (data[c])].shape[0]
                #divide them by the total occurances of code r
                #to get how often we see c given we see r
                dp.ix[r, c] = together / alone
    
    return dp.drop(['count', 'frequency', 'var'], axis=1)

def krippendorff(data, stats):
    '''Calculate the Krippendorff alpha statistic for each pair of
    codes. Follows:
        [this paper](http://repository.upenn.edu/cgi/viewcontent.cgi?article=1043&context=asc_papers)
    '''
    cols = data.columns.values
    dp = stats.copy()
    n = data.shape[0]

    for r in cols: #rows
        for c in cols: #columns
            count_r = stats.ix[r, 'count']
            count_c = stats.ix[c, 'count']
            both = data[(data[r]) & (data[c])].shape[0]
            xor = count_r + count_c - (both * 2)
            neither = n - both - xor
            #count each pair twice
            both = both * 2
            xor = xor * 2
            neither = neither * 2
            
            dp.ix[r, c] = 1 - ( (n-1) * (xor / 
                                         ((neither + xor) * (xor + both)) ) )
    
    return dp.drop(['count', 'frequency', 'var'], axis=1)

def directed_normed_z(real, rand, stats, n):
    '''Compute the normalized difference between the observed
    cooccurrance rates and those expected under the assumption of
    independence, for directed graphs. 
    '''
    #use our predicted cooccurrance matrix as a template
    cols = rand.columns.values
    z = rand.copy()

    for r in cols: #rows
        for c in cols: #columns
            #difference between actual and predicted values
            diff = (real.ix[r, c] - rand.ix[r, c]) 
            
            #pooled stddiv between overall rate and conditional rate
            stdiv = sqrt( var(stats.ix[c, 'frequency'], n) + 
                      var(real.ix[r, c], stats.ix[r, 'count']) )
            
            #z-scores 
            z.ix[r, c] = diff / stdiv
    
    return z

def directed_lift(real, rand, stats, n):
    '''Compute the lift for rules of the form A -> B for all
    combinations of codes A, B. Lift > 1 implies positive association.
    '''
    #use our predicted cooccurrance matrix as a template
    cols = rand.columns.values
    lift = rand.copy()

    for r in cols: #rows
        for c in cols: #columns
            try:
                lift.ix[r, c] = (real.ix[r, c] / rand.ix[r, c]) 
            except ZeroDivisionError:
                lift.ix[r, c] = float('NaN')
    
    return lift

def norm_cooccur(data, directed=False):
    '''normalize the cooccurance rates to z scores
    H0: codes are independent 
    '''
    stats = get_freq(data)
    
    if directed:
        dp = directed_proportions(data, stats)
        dr = directed_random(data, stats)
        z = directed_normed_z(dp, dr, stats, n=data.shape[0])
        
    else:
        rand = rand_cooccur(data, stats)
        real = real_cooccur(data, stats)
        z = normed_diff(rand, real, stats)
    
    return z

def reverse(data):
    '''cooccurrance shows affinity between codes, they happen together
    more than we expect. However, the opposite effect is also interesting.
    Reversing the signs on our weights gives a graph of codes that repell 
    one another.
    '''
    return data.applymap(lambda x: -1 * x)












