# @author Jeff Lockhart <jwlock@umich.edu>
# utility functions for making network graphs out of code/tag applications in qualitative data
# version 0.1

import pandas as pd
import networkx as nx
from math import sqrt

def make_net(data, min_weight=0, isolates=False):
    """Create a networkx network from our dataframe of edge weights
    Input:
        data: a symmetric pandas data frame of edge weights
        min_weight: ignore weights at or below this number
        isolates: boolean, do we include nodes without edges?
    """
    #create an empty graph and get a list of nodes
    g = nx.Graph()
    nodes = data.columns.values
    
    #if we want to include even nodes without edges
    if isolates:
        g.add_nodes_from(nodes)
    
    #iterate over the upper triangle of the data matrix
    for i in range(len(nodes)): #rows
        for j in range(i+1, len(nodes)): #columns
            #check whether this edge should exist
            if data.ix[nodes[i], nodes[j]] > min_weight: 
                #adding the edge also adds the nodes if they are 
                #not yet present
                g.add_edge(nodes[i], nodes[j], 
                           weight = data.ix[nodes[i], nodes[j]])

    return g

def sdiv(x,n):
    """standard deviation for proportion"""
    return sqrt(abs(x*(1-x))/n)

def get_freq(data):
    """Compute the frequencies of each code/column
    """
    rows = 1.0 * data.shape[0] #number of rows as float
    cols = data.columns.values
    stats = pd.DataFrame()
    
    stats['count'] = data[cols].sum(axis=0, numeric_only=True)
    stats['frequency'] = stats['count'] / rows   
    stats['sdiv'] = stats['frequency'].apply(sdiv, n=rows)
    
    return stats

def rand_cooccur(data, stats):
    """Compute the probability of any two codes cooccurring, assuming 
    the codes are independent.
    """
    cols = data.columns.values
    rand_co = stats.copy()
    
    #create columns for each code as the probability of cooccurance
    #with the code in each row, assuming independence
    for c in cols:
        rand_co[c] = rand_co['frequency'] * stats.ix[c, 'frequency']
    
    #drop vestigial columns from stats df
    return rand_co.drop(['count', 'frequency', 'sdiv'], axis=1)
    
def real_cooccur(data, stats):
    """Compute how often we observe codes together in the real data.
    """
    cols = data.columns.values
    real_co = stats.copy()
    rows = 1.0 * data.shape[0] #rows as float
    
    for r in cols: #rows
        for c in cols: #columns
            #set this cell to the number of rows with both codes
            #TODO: normalize this better than by row count
            real_co.ix[r, c] = data[(data[r]) & 
                                  (data[c])].shape[0] / rows
    
    #drop vestigial columns from stats df
    return real_co.drop(['count', 'frequency', 'sdiv'], axis=1)

def normed_diff(rand, real, stats):
    """Compute the normalized difference between the observed
    cooccurrance rates and those expected under the assumption of
    independence. 
    """
    #use our predicted cooccurrance matrix as a template
    cols = rand.columns.values
    z = rand.copy()

    for r in cols: #rows
        for c in cols: #columns
            #difference between actual and predicted values
            diff = (real.ix[r, c] - rand.ix[r, c]) 
            #standard deviation under null hypothesis
            stdiv = sqrt((stats.ix[r, 'sdiv']**2) + 
                                   (stats.ix[c, 'sdiv']**2))
            #z-scores 
            z.ix[r, c] = diff / stdiv
    
    return z 

def norm_cooccur(data):
    """normalize the cooccurance rates to z scores
    H0: codes are independent 
    """
    stats = get_freq(data)
    rand = rand_cooccur(data, stats)
    real = real_cooccur(data, stats)
    z = normed_diff(rand, real, stats)
    
    return z

def reverse(data):
    """cooccurrance shows affinity between codes, they happen together
    more than we expect. However, the opposite effect is also interesting.
    Reversing the signs on our weights gives a graph of codes that repell 
    one another.
    """
    return data.applymap(lambda x: -1 * x)










