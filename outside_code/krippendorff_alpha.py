'''
Python implementation of Krippendorff's alpha -- inter-rater reliability

(c)2011 Thomas Grill (http://grrrr.org)
license: http://creativecommons.org/licenses/by-sa/3.0/

Python version >= 2.4 required
downloaded from: http://grrrr.org/data/dev/krippendorff_alpha/krippendorff_alpha.py
'''

try:
    import numpy as N
except ImportError:
    N = None

def nominal_metric(a,b):
    return a != b

def interval_metric(a,b):
    return (a-b)**2

def ratio_metric(a,b):
    return ((a-b)/(a+b))**2

def krippendorff_alpha(data,metric=interval_metric,force_vecmath=False,convert_items=float,missing_items=None):
    '''
    Calculate Krippendorff's alpha (inter-rater reliability):
    
    data is in the format
    [
        {unit1:value, unit2:value, ...},  # coder 1
        {unit1:value, unit3:value, ...},   # coder 2
        ...                            # more coders
    ]
    or 
    it is a sequence of (masked) sequences (list, numpy.array, numpy.ma.array, e.g.) with rows corresponding to coders and columns to items
    
    metric: function calculating the pairwise distance
    force_vecmath: force vector math for custom metrics (numpy required)
    convert_items: function for the type conversion of items (default: float)
    missing_items: indicator for missing items (default: None)
    '''
    
    # number of coders
    m = len(data)
    
    # set of constants identifying missing values
    maskitems = set((missing_items,))
    #if N is not None:
        #This seems to be broken. I have disabled because I don't need it.
        #maskitems.add(N.ma.masked_singleton)
    
    # convert input data to a dict of items
    units = {}
    for d in data:
        try:
            # try if d behaves as a dict
            diter = d.iteritems()
        except AttributeError:
            # sequence assumed for d
            diter = enumerate(d)
            
        for it,g in diter:
            if g not in maskitems:
                try:
                    its = units[it]
                except KeyError:
                    its = []
                    units[it] = its
                its.append(convert_items(g))


    units = dict((it,d) for it,d in units.iteritems() if len(d) > 1)  # units with pairable values
    n = sum(len(pv) for pv in units.itervalues())  # number of pairable values
    
    N_metric = (N is not None) and ((metric in (interval_metric,nominal_metric,ratio_metric)) or force_vecmath)
    
    Do = 0.
    for grades in units.itervalues():
        if N_metric:
            gr = N.array(grades)
            Du = sum(N.sum(metric(gr,gri)) for gri in gr)
        else:
            Du = sum(metric(gi,gj) for gi in grades for gj in grades)
        Do += Du/float(len(grades)-1)
    Do /= float(n)

    De = 0.
    for g1 in units.itervalues():
        if N_metric:
            d1 = N.array(g1)
            for g2 in units.itervalues():
                De += sum(N.sum(metric(d1,gj)) for gj in g2)
        else:
            for g2 in units.itervalues():
                De += sum(metric(gi,gj) for gi in g1 for gj in g2)
    De /= float(n*(n-1))

    return 1.-Do/De

if __name__ == '__main__': 
    print "Example from http://en.wikipedia.org/wiki/Krippendorff's_Alpha"

    data = (
        "*    *    *    *    *    3    4    1    2    1    1    3    3    *    3", # coder A
        "1    *    2    1    3    3    4    3    *    *    *    *    *    *    *", # coder B
        "*    *    2    1    3    4    4    *    2    1    1    3    3    *    4", # coder C
    )

    missing = '*' # indicator for missing values
    array = [d.split() for d in data]  # convert to 2D list of string items
    
    print "nominal metric: %.3f" % krippendorff_alpha(array,nominal_metric,missing_items=missing)
    print "interval metric: %.3f" % krippendorff_alpha(array,interval_metric,missing_items=missing)
