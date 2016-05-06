# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 18:57:25 2015

@author: Colin

Round Robin scheduler: https://en.wikipedia.org/wiki/Round-robin_tournament

"""

import string

N = 13 # Number of teams to schedule

names = list(string.ascii_uppercase)[:N]
        

if len(names) % 2 == 1:
    names.append('bye')
    
for ii in range(len(names)):
    print("")
    print("Round " + str(ii))
    for jj in range(len(names)/2):
        print(names[jj] + " + " + names[len(names) - jj - 1])
    names.insert(1,names[-1])
    names = names[:-1]
