# -*- coding: utf-8 -*-
"""
Created on Tue Jan 27 16:56:03 2015

@author: Colin
"""

import numpy as np
import random

# Random matrix for testing
N = 20
weights = 10*np.random.rand(N,N)

"""
weights = np.array([[0, 1, 2, 3, 4, 5],
                    [1, 0, 3, 4, 5, 6],
                    [1, 1, 0, 1, 1, 1], 
                    [10, 9, 8, 0, 10, 6],
                    [4, 5, 4, 5, 0, 5],
                    [6, 5, 4, 3, 2, 0]])
N = len(weights)
"""

print(weights)

weightsT = np.transpose(weights)

print("")
print(weights * weightsT)

# Random matching

M = 1000 # iterations
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
        
    cost = np.mean(cost_list)
    #cost = np.min(cost_list)
    #cost = np.median(cost_list)

    if cost > cost_max:
        cost_max = cost
        print("")
        print(str(m) + '/' + str(M))
        print(pairs)
        print(cost)
        print("")
