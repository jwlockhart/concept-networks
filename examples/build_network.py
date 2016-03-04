# @author Jeff Lockhart <jwlock@umich.edu>
# Example script for cleaning and reformatting Dedoose excerpt export files. 
# version 1.1

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import sys
#add the parent directory to the current session's path
sys.path.insert(0, '../')
#import utility file from parent directory
from network_utils import *

argv = sys.argv
if len(argv) != 2:
    print 'Please run this script with exactly 1 argument.\n$ build_network.py [infile.tsv]'
    sys.exit()

#Import our data from Dedoose
print 'Reading in data...'
df = pd.read_csv(argv[1], sep='\t')

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

print "Computing co-occurrance statistics..."
z = norm_cooccur(df[code_cols], directed=False)
z_dir =norm_cooccur(df[code_cols], directed=True)

print "Generating network..."
g = make_net(data=z, min_weight=1, isolates=False, directed=False)
g_dir = make_net(data=z_dir, min_weight=1, isolates=False, directed=True)

def show_graph(g):
    """Display our network. Customize to best suit your own needs."""
    #canvas setup. figsize is in inches. 
    plt.figure(figsize=(12,12))

    #layout nodes and their labels
    pos=nx.spring_layout(g)
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

    plt.show()

print "Drawing undirected network..."
show_graph(g)

print "Drawing directed network..."
show_graph(g_dir)


#reverse network example
diff_r = reverse(diff)
g_r = make_net(data=diff_r, min_weight=0, isolates=False)


print "Done!"























