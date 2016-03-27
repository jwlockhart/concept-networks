# @author Jeff Lockhart <jwlock@umich.edu>
# Actual script used to generate network diagrams in drafts of 
# the project paper for which this code is written.
# version 1.0

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import sys
#add the parent directory to the current session's path
sys.path.insert(0, '../')
#import utility file from parent directory
from network_utils import *

#The list of codes we're interested in. 
code_cols = ['culture_problem', 
             #'culture_absent', 
             'culture_solution', 
             'culture_helpless', 
             'culture_victim', 
             'cishet_problem', 
             'cishet_victim', 
             'cishet_solution', 
             #'cishet_absent', 
             'cishet_helpless', 
             'sgm_victim', 
             'sgm_problem', 
             'sgm_helpless', 
             #'sgm_absent', 
             'sgm_solution', 
             'school_problem', 
             'school_solution', 
             #'school_absent', 
             'school_victim', 
             'school_helpless', 
             'community_problem', 
             'community_solution', 
             'community_helpless', 
             #'community_absent', 
             'community_victim']

def gen_net(df):
    tmp = get_freq(df[code_cols])
    #drop codes applied less than 10 times
    df = df[tmp[tmp['count'] >= 10].index.values]
    #compute cooccurance stats
    z = norm_cooccur(df, directed=True)
    #create network
    g = make_net(data=z, min_weight=1, isolates=True, directed=True)
    return g

def show_graph(g, pos, save_to='out.png'):
    '''Display our network. Customize to best suit your own needs.'''
    #canvas setup. figsize is in inches. 
    plt.figure(figsize=(12,12))

    nx.draw_networkx_nodes(g, pos, node_size=400)
    nx.draw_networkx_labels(g, pos, font_size=14, font_family='sans-serif')

    #divide edges into groups based on weight
    #i.e. statistical significance of cooccurance
    e999 =[(u, v) for (u, v, d) in g.edges(data=True) if 
           (d['weight'] >= 3.291)]
    e990 =[(u, v) for (u, v, d) in g.edges(data=True) if 
           (d['weight'] < 3.291) & (d['weight'] >= 2.576)]
    e950 =[(u, v) for (u, v, d) in g.edges(data=True) if 
           (d['weight'] < 2.576) & (d['weight'] >= 1.96)]
    e841 =[(u, v) for (u, v, d) in g.edges(data=True) if 
           (d['weight'] < 1.96) & (d['weight'] >= 1)]

    #draw edges in each group
    nx.draw_networkx_edges(g, pos, edgelist=e999, width=6, alpha=0.5)
    nx.draw_networkx_edges(g, pos, edgelist=e990, width=2, alpha=0.5)
    nx.draw_networkx_edges(g, pos, edgelist=e950, width=2, alpha=0.5,
                           edge_color='b')
    nx.draw_networkx_edges(g, pos, edgelist=e841, width=2, alpha=0.5,
                           edge_color='b', style='dashed')

    #axes look silly here
    plt.axis('off')
    
    plt.savefig(save_to)
    #plt.show()


#Import our answer-level data
print 'Reading in answer data...'
merged = pd.read_csv('../data/merged.tsv', sep='\t')
ben = pd.read_csv('../data/ben.tsv', sep='\t')
gabi = pd.read_csv('../data/gabi.tsv', sep='\t')

print 'Generating answer networks...'
g_merged = gen_net(merged)
g_ben = gen_net(ben)
g_gabi = gen_net(gabi)
    
print 'Drawing answer networks...'
#fix the positions of nodes to the the same in all networks
p = nx.spring_layout(g_merged)
#pos=nx.circular_layout(g)
#pos=nx.random_layout(g)
#pos=nx.shell_layout(g)
#pos=nx.spectral_layout(g)
    
show_graph(g_merged, p, '../data/di_ans_merged.png')
show_graph(g_ben, p, '../data/di_ans_ben.png')
show_graph(g_gabi, p, '../data/di_ans_gabi.png')


#import data aggregated to person-level
print 'Reading in person data...'
merged = pd.read_csv('../data/merged_person.tsv', sep='\t')
ben = pd.read_csv('../data/ben_person.tsv', sep='\t')
gabi = pd.read_csv('../data/gabi_person.tsv', sep='\t')

print 'Generating person networks...'
g_merged = gen_net(merged)
g_ben = gen_net(ben)
g_gabi = gen_net(gabi)
    
print 'Drawing person networks...'
#fix the positions of nodes to the the same in all networks
#p = nx.spring_layout(g_merged)
p = nx.circular_layout(g_merged)
#pos=nx.random_layout(g)
#pos=nx.shell_layout(g)
#pos=nx.spectral_layout(g)
    
show_graph(g_merged, p, '../data/di_per_merged.png')
show_graph(g_ben, p, '../data/di_per_ben.png')
show_graph(g_gabi, p, '../data/di_per_gabi.png')

print 'Done!'







