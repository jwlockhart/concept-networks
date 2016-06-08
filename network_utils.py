# @author Jeff Lockhart <jwlock@umich.edu>
# utility functions for making network graphs out of code/tag 
# applications in qualitative data
# version 2.0

import pandas as pd
import networkx as nx
from math import sqrt

def make_net_list(data, idx1='i', idx2='j', idx3='Jaccard', min_weight=0):
    g = nx.Graph()
    
    for row in data.iterrows():
        w = row[1][idx3]
        if w > min_weight:
            g.add_edge(row[1][idx1], row[1][idx2], weight = w)  
    
    return g

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
    n = float(n)
    return abs(x*(1-x))/n

def sdiv(x,n):
    '''standard deviation for proportion'''
    return sqrt(var(x,n))

def get_freq(data):
    '''Compute the frequencies of each code/column'''
    rows = 1.0 * data.shape[0] #number of rows as float
    cols = data.columns.values
    stats = pd.DataFrame()
    
    stats['count'] = data.sum()
    stats['frequency'] = data.mean()
    stats['var'] = stats['frequency'].apply(var, n=data.shape[0])
    
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
    '''Compute how often we observe codes together in the real data.'''
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

def jaccard(a, b):
    '''Jaccard similarity index for two vectors'''
    n = len(a)
    union = 0.0
    intersection = 0.0
    #iterate over vector elements
    for i in range(0, n):
        #if at least one has a code
        if a[j] | b[j]:
            intersection = intersection + 1
            #if both have the code
            if a[j] & b[j]:
                union = union + 1
    
    result = 0.0
    if intersection > 0:
        result = union / intersection
    
    return result

def all_v_all_jaccard_sim(df):
    '''Serial implementation of all v all Jaccard similarity.
    Slow, space intensive. Reccomended only for small data sets.
    Used here to compute the edge weights on a network that is the 
    projection from codes onto people or onto answers.
    '''
    #add a unique ID column
    n = len(df) + 1
    idx = range(1, n)
    df['uid'] = idx
    id_map = df[['uid']]
    df = df.set_index(['uid'])
    
    data = df.transpose()
    result = pd.DataFrame(0, index=idx, columns=idx)
    
    for i in range(1, n):
        if i % 50 == 0:
            print (i*100.0)/n, '% of', n, 'done...'
        for j in range(1, i):
            result.ix[i, j] = jaccard(data[i], data[j])
    
    return (id_map, result)

def parallel_jaccard(dic):
    '''Map function to be used in parallel computation of 
    all v all jaccard similarity. Individual pairwise comparisons
    proved to be too small of jobs for decent parallel computation.
    Thus, each job compares one element i to all other elements 
    in range(0, i).
    For space efficiency, a dictionary of non-zero scores is returned
    instead of an adjacency matrix.
    '''
    #what column to use as our reference
    i = dic['i']
    #our data
    data = dic['dat']
    a = data[i]
    #the number of codes we're comparing across columns
    codes = data.shape[0]

    output = {}
    
    #loop over all the columns we need to compare
    for k in range(0, i):
        #temp variables
        union = 0.0
        intersection = 0.0
        b = data[k]
        #loop over the codes to compare in these cols
        for j in range(0, codes):
            #if at least one has a code
            if a[j] | b[j]:
                intersection = intersection + 1
                #if both have the code
                if a[j] & b[j]:
                    union = union + 1
        #only save scores > 0
        if (intersection > 0) & (union > 0):
            output[k] = (union / intersection) 
            
    return {'i':i, 'Jaccard':output}

def list_people_data(df):
    '''Generates a list of input to be mapped to parallel_jaccard().'''
    #add a unique ID column
    n = len(df)
    idx = range(0, n)
    df['uid'] = idx
    id_map = df[['uid']]
    df = df.set_index(['uid'])
    #transpose data frame for easier indexing
    data = df.transpose()
    result = []
    #create a list of jobs where each job is an element and a
    #set of other elements to compare it with.
    for i in range(0, n):
        dic = {'i':i, 'dat':data.ix[:,0:i]}
        result.append(dic)
            
    return (id_map, result)








