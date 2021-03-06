# -*- coding: utf-8 -*-
"""
Created on Tue Jan 27 16:56:03 2015

@author: Colin

This is a very quick and dirty way of finding optimal pairings based on 
asymmetric and complete pairwise ratings.  Full stochastic, but what's life 
without a little luck?

"""

import numpy as np
import random


testFlag = False
costFunction = 'mean' # options are 'mean', 'median', 'min'


if testFlag:
    # Random matrix for testing
    N = 20
    weights = 10*np.random.rand(N,N)

else:
    weights = np.array([[0,6,10,9,7,10,9,4,4,8,8,6,6,8,8,9,8,9,6,4,0,5,7,0,7,4],
    [10,0,8,9,6,10,9,6,6,7,8,0,9,8,9,9,0,8,8,6,7,6,6,7,7,8],
    [9,9,0,8,7,8,8,6,8,7,7,7,10,8,8,9,10,9,8,7,10,9,8,7,9,8],
    [9,7,8,10,8,9,9,4,6,8,7,6,8,9,5,8,9,8,7,6,9,9,7,8,8,8],
    [8.5,7,7,7,0,8,7,4,7,7,7,6,8.5,7.5,6,7.5,8,8.5,8,8,8.5,6,7,6.5,7,8],
    [0,8,4,8.9,7,0,6.9,6,8.8,10,8,7,3.14,8.5,7,8,5,9.2,7,8,0,6.78,5,9,8.9,7.89],
    [6,9,7,8,7,7,0,8,9,10,0,9,7,6,8,4,8,7,5,4,7,3,8,5,6,4],
    [8,7,9,8,0,7,7,0,0,2,7,8,7,4,5,0,6,0,7.5,6,4,9,7,6,7,2],
    [7,7,8,6,6,8,8,0,0,5,6,8,6,7,4,8,7,5,8,6,7,7,6,6,6,7],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,8,9,6,8,8,0,8,0,10,0,6,9,6,8,10,8,7,9,0,9,6,9,7,0,8],
    [10,7,8,9,7,7,10,8,7,8,7,0,9,0,7,9,10,9,10,8,0,8,7,6,10,0],
    [7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7],
    [10,8,9,10,4,9,7,8,0,10,5,10,9,0,8,10,10,10,0,0,9,10,7,4,0,10],
    [10,7,8.1,6.4,6,10,9,6.4,5.2,7.8,8.4,4.5,8.9,7,10,7.5,9.2,9.3,0,8.8,9,10,8.1,7.8,3,10],
    [9,9,0,9,9,7,7.5,6,8,7,7,6,8,8,7,10,0,8,9,9,9,7,9,0,9,7],
    [9,5,10,9,4,10,10,3,9,8,4,6,8,10,10,8,0,9,5,5,10,4,9,5,10,7],
    [7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7],
    [8,8,10,7,7,9,8,6,8,7,9,10,9,8,9,9,9,10,0,9,8,7,7,8,10,10],
    [8,7,9,8,9,9,9,8,8,8,0,9,9,10,9,8,7,8,10,0,8,9,8,9,7,0],
    [10,4,10,10,3,10,4,5,6,10,8,7,10,4,10,9,10,10,9,6,10,9,10,10,5,4],
    [8,4,9,7,5,6,7,5,8,10,3,10,10,10,7,8,7,10,7,8,7,0,8,0,7,7],
    [8.2,8.2,8.2,8.1,6,8.1,8.1,5.5,7.5,8,6.5,8.4,7.9,6.4,8.1,8.4,8.1,8.2,7.9,8,8.3,8.1,0,7.3,7.5,7.8],
    [9,8,9,6,6,7,5,8,6,4,6,5,7,3,5,10,9,8,7,7,7,7,6,0,9,7],
    [8,7,0,9,8,9,9,8,0,8,8,9,7,9,9,9,7,8,8,8,8,8,8,7,0,8],
    [8,8,9,8,9,9,7,5,6,9,6,9,9,9,9,7,9,9,9,8,8,5,7,5,6,10]])
    N = len(weights)


print(weights)

weightsT = np.transpose(weights)

print("")
print(weights * weightsT)

# Random matching

M = 10000 # iterations
cost_max = 0
for m in range(M):
    #print(str(m) + '/' + str(M))
    
    w = np.sqrt(weights * weightsT)
    index = range(N)
    pairs = []
    cost_list = []
    
    while len(w) > 1:
    
        n = len(w)
        x_range = range(n)
        x = random.choice(x_range)
        x_range.remove(x)
        y = random.choice(x_range)
        
        #print(w[x,y])
        
        cost_list.append(w[x,y])
        
        w = np.delete(w, [x, y], 0)
        w = np.delete(w, [x, y], 1)
        
        pairs.append((index[x],index[y]))
        index = np.delete(index, [x,y])
        
    if costFunction == 'mean':
        cost = np.mean(cost_list)
    elif costFunction == 'min':
        cost = np.min(cost_list)
    elif costFunction == 'median':
        cost = np.median(cost_list)
    else: # default to mean
        cost = np.mean(cost_list)

    if cost > cost_max:
        cost_max = cost
        print("")
        print(str(m) + '/' + str(M))
        print(pairs)
        print(cost)
        print("")
