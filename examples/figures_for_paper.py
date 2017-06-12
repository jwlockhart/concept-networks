# @author Jeff Lockhart <jwlock@umich.edu>
# Actual script used to generate network diagrams in drafts of 
# the project paper for which this code is written.
# version 1.2

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import sys
#add the parent directory to the current session's path
sys.path.insert(0, '../')
#import utility file from parent directory
from network_utils import *
import nlp

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

def gen_net(df, directed=True):
    tmp = get_freq(df[code_cols])
    #drop codes applied less than 10 times
    df = df[tmp[tmp['count'] >= 10].index.values]
    #compute cooccurance stats
    z = norm_cooccur(df, directed=directed)
    #create network
    g = make_net(data=z, min_weight=1, directed=directed)
    return g

def show_graph(g, pos, save_to='out.png', ti='title'):
    '''Display our network. Customize to best suit your own needs.'''
    #canvas setup. figsize is in inches. 
    plt.figure(figsize=(25,25))

    nx.draw_networkx_nodes(g, pos, node_size=10000, node_color='w')
    nx.draw_networkx_labels(g, pos, font_size=12, font_family='sans-serif')

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

    plt.title(ti)
    #axes look silly here
    plt.axis('off')
    
    plt.savefig(save_to)
    #plt.show()


#Import our answer-level data
print('Reading in answer data...')
merged = pd.read_csv('../data/sgm_stud/merged.tsv', sep='\t')
ben = pd.read_csv('../data/sgm_stud/ben.tsv', sep='\t')
gabi = pd.read_csv('../data/sgm_stud/gabi.tsv', sep='\t')

print('Generating answer networks...')
g_merged = gen_net(merged)
g_ben = gen_net(ben)
g_gabi = gen_net(gabi)

g_merged_un = gen_net(merged, directed=False)
    
print('Drawing answer networks...')
#fix the positions of nodes to the the same in all networks
layout = g_merged.copy()
layout.add_nodes_from(merged.columns.values)
p = nx.spring_layout(layout)
#pos=nx.circular_layout(g)
#pos=nx.random_layout(g)
#pos=nx.shell_layout(g)
#pos=nx.spectral_layout(g)
    
show_graph(g_merged, p, '../data/sgm_stud/di_ans_merged.png', ti='Per-answer All Coders')
show_graph(g_ben, p, '../data/sgm_stud/di_ans_ben.png', ti='Per-answer Ben')
show_graph(g_gabi, p, '../data/sgm_stud/di_ans_gabi.png', ti='Per-answer Gabi')

show_graph(g_merged_un, p, '../data/sgm_stud/un_ans_merged.png', ti='Per-person All Coders')

#import data aggregated to person-level
print('Reading in person data...')
merged = pd.read_csv('../data/sgm_stud/merged_person.tsv', sep='\t')
ben = pd.read_csv('../data/sgm_stud/ben_person.tsv', sep='\t')
gabi = pd.read_csv('../data/sgm_stud/gabi_person.tsv', sep='\t')

print('Generating person networks...')
g_merged = gen_net(merged)
g_ben = gen_net(ben)
g_gabi = gen_net(gabi)

g_merged_un = gen_net(merged, directed=False)
    
print('Drawing person networks...')
    
show_graph(g_merged, p, '../data/sgm_stud/di_per_merged.png', ti='Per-person All Coders')
show_graph(g_ben, p, '../data/sgm_stud/di_per_ben.png', ti='Per-person Ben')
show_graph(g_gabi, p, '../data/sgm_stud/di_per_gabi.png', ti='Per-person Gabi')

show_graph(g_merged_un, p, '../data/sgm_stud/un_per_merged.png', ti='Per-person All Coders')

#Import our answer-level data for cishet people
print('Reading in answer data...')
merged = pd.read_csv('../data/ch_stud/merged.tsv', sep='\t')
ben = pd.read_csv('../data/ch_stud/ben.tsv', sep='\t')
gabi = pd.read_csv('../data/ch_stud/gabi.tsv', sep='\t')

print('Generating answer networks...')
g_merged = gen_net(merged)
g_ben = gen_net(ben)
g_gabi = gen_net(gabi)
    
g_merged_un = gen_net(merged, directed=False)
    
print('Drawing answer networks...')
show_graph(g_merged, p, '../data/ch_stud/di_ans_merged.png', ti='Per-answer All Coders')
show_graph(g_ben, p, '../data/ch_stud/di_ans_ben.png', ti='Per-answer Ben')
show_graph(g_gabi, p, '../data/ch_stud/di_ans_gabi.png', ti='Per-answer Gabi')

show_graph(g_merged_un, p, '../data/ch_stud/un_ans_merged.png', ti='Per-person All Coders')

print('Drawing NLP networks...')

text_col = 'Excerpt Copy'
df = pd.read_csv('../data/ben_all.tsv', sep='\t')

'''Remove the labels Dedoose adds. Generally, they follow
the form 'Question: xxx; Answer:'. In my particular data,
all questions 'xxx' match the regex 'Q\d*\w?'. You will need to 
modify this regex to work with your question labels. Alternatively, 
you could omit this step, but then the similarity of your documents
would be biased in favor of those with more of the same questions.
'''
df = df.replace({'Question: Q\d*\w?; Answer:': ''}, regex=True)
documents = nlp.make_docs(df, code_cols, text_col)
cs = nlp.cosine_sim_pd(docs=documents, codes=code_cols)
g = make_net(data=cs, min_weight=0.75, isolates=False, directed=False)

def show_graph_nlp(g, save_to='test.png'):
    '''Display our network. Customize to best suit your own needs.'''
    plt.figure(figsize=(25,25))
    
    #layout nodes and their labels
    pos=nx.spring_layout(g)
    nx.draw_networkx_nodes(g, pos, node_size=10000, node_color='w')
    nx.draw_networkx_labels(g, pos, font_size=12, font_family='sans-serif')

    #divide edges into groups based on weight
    #i.e. statistical significance of cooccurance
    e999 =[(u, v) for (u, v, d) in g.edges(data=True) if 
           (d['weight'] >= 0.9)]
    e990 =[(u, v) for (u, v, d) in g.edges(data=True) if 
           (d['weight'] < 0.9) & (d['weight'] >= 0.75)]
    e950 =[(u, v) for (u, v, d) in g.edges(data=True) if 
           (d['weight'] < 0.75) & (d['weight'] >= 0.5)]
    e841 =[(u, v) for (u, v, d) in g.edges(data=True) if 
           (d['weight'] < 0.5) & (d['weight'] >= 0.25)]
    
    #draw edges in each group
    nx.draw_networkx_edges(g, pos, edgelist=e999, width=6, alpha=0.5)
    nx.draw_networkx_edges(g, pos, edgelist=e990, width=2)#, alpha=0.5)
    #nx.draw_networkx_edges(g, pos, edgelist=e950, width=2, alpha=0.5,
    #                       edge_color='b')
    #nx.draw_networkx_edges(g, pos, edgelist=e841, width=2, alpha=0.5,
    #                       edge_color='b', style='dashed')

    #axes look silly here
    plt.axis('off')

    plt.savefig(save_to)
    
show_graph_nlp(g, '../data/nlp_net.png')
    
print('Done!')







