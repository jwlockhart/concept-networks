# concept-networks

This repo contains code for runing network-based analyses of codes applied to qualitative data. In short, the goal is to map the relationships between concepts in qualitative data in a graph/network structure. For an example of such analyses, see:

Ghaziani, Amin and Delia Baldassarri. 2011. "Cultural Anchors and the Organization of Differences: A Multi-Method Analysis of LGBT Marches on Washington." *American Sociological Review* 76(2):179–206.

All code for this project will use open-source libraries rather than proprietary network analysis and statistical software. Initial qualitative coding of the data was done by a team of research assistants working on separate clones of a [Dedoose](http://www.dedoose.com) project. The excerpts and their codes are exported as csv files and then compared to calculate metrics of inter-rater reliabilityand resolve disagreements before the codes are used to generate networks for analysis. 

**Packages:**
- pandas
- networkx
- matplotlib
- re
- sys
- math
- ntlk
- string
- sklearn
