# @author Jeff Lockhart <jwlock@umich.edu>
# utility functions for making network graphs out of code/tag applications in qualitative data
# version 0.1

import pandas as pd
import networkx as nx

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

def get_freq(data):
    """Compute the frequencies of each code/column
    """
    cols = data.columns.values
    stats = pd.DataFrame()
    stats['count'] = data[cols].sum(axis=0, numeric_only=True)
    stats['frequency'] = stats['count'] / data.shape[0]    
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
    return rand_co.drop(['count', 'frequency'], axis=1)
    
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
    return real_co.drop(['count', 'frequency'], axis=1)

def normed_diff(rand, real):
    """Compute the normalized difference between the observed
    cooccurrance rates and those expected under the assumption of
    independence. 
    """
    #use our predicted cooccurrance matrix as a template
    cols = rand.columns.values
    diff = rand.copy()

    for r in cols: #rows
        for c in cols: #columns
            #cells are the difference between actual and 
            #predicted values, normalized by predicted values
            diff.ix[r, c] = (real.ix[r, c] - 
                             rand.ix[r, c]) / rand.ix[r, c]
    
    return diff

def norm_cooccur(data):
    """
    """
    stats = get_freq(data)
    rand = rand_cooccur(data, stats)
    real = real_cooccur(data, stats)
    diff = normed_diff(rand, real)
    
    return diff












