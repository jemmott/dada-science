# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 09:21:34 2014
CWJ
"""

import csv
import json
import wordCloudHTML
import scipy.spatial
import numpy as np

# DATA IMPORT
with open('Virtue Data Jan 2014.csv', 'rb') as csvfile:
    virtuereader = csv.reader(csvfile, delimiter=',')
    firstRow = True
    data = []
    labels = []
    category = []
    for row in virtuereader:
        if firstRow:
            labels = [x for x in row[1:23]]
            firstRow = False
        else:
            category.append(row[0])
            x = []
            for datum in row[1:23]:
                if datum:
                    x.append(int(datum))
                else:
                    x.append(0)
            data.append(x)

# WORD CLOUD
wordJson = []
for ii in range(len(category)):
    if sum(data[ii]) > 1:
        x = {}
        x['text'] = category[ii]
        x['size'] = 15+0.5*sum(data[ii])**1.2
        wordJson.append(x)
outfile = open('Results/all_words.html', 'w+')
outfile.write(wordCloudHTML.header())
outfile.write(json.dumps(wordJson))
outfile.write(wordCloudHTML.footer())
outfile.close()

cluster1index = np.subtract([1,3,6,11,16,19,21],1)
cluster2index = np.subtract([5,18,17,22,2,7,10,8,13,14],1)
cluster3index = np.subtract([9,20,4,15,12],1)

wordJson = []
for ii in range(len(category)):
    weight = 0
    for index in cluster1index:
        weight = weight + data[ii][index]
    if weight > 1:
        x = {}
        x['text'] = category[ii]
        x['size'] = 15+(200*weight/(sum(data[ii]*len(cluster1index))))**1.2
        #x['size'] = 15+(15*weight/len(cluster1index))**1.2
        wordJson.append(x)
outfile = open('Results/orangeCluster.html', 'w+')
outfile.write(wordCloudHTML.header())
outfile.write(json.dumps(wordJson))
outfile.write(wordCloudHTML.footer())
outfile.close()

wordJson = []
for ii in range(len(category)):
    weight = 0
    for index in cluster2index:
        weight = weight + data[ii][index]
    if weight > 1:
        x = {}
        x['text'] = category[ii]
        x['size'] = 15+(200*weight/(sum(data[ii]*len(cluster2index))))**1.2
        #x['size'] = 15+(15*weight/len(cluster2index))**1.2
        wordJson.append(x)
outfile = open('Results/whiteCluster.html', 'w+')
outfile.write(wordCloudHTML.header())
outfile.write(json.dumps(wordJson))
outfile.write(wordCloudHTML.footer())
outfile.close()

wordJson = []
for ii in range(len(category)):
    weight = 0
    for index in cluster3index:
        weight = weight + data[ii][index]
    if weight > 1:
        x = {}
        x['text'] = category[ii]
        x['size'] = 15+(200*weight/(sum(data[ii]*len(cluster3index))))**1.2
        #x['size'] = 15+(15*weight/len(cluster3index))**1.2
        wordJson.append(x)
outfile = open('Results/purpleCluster.html', 'w+')
outfile.write(wordCloudHTML.header())
outfile.write(json.dumps(wordJson))
outfile.write(wordCloudHTML.footer())
outfile.close()

# Cloud for one person
index = 15-1
wordJson = []
for ii in range(len(category)):
    weight = data[ii][index]
    if weight > 0:
        x = {}
        x['text'] = category[ii]
        x['size'] = 15+(10*weight)
        #x['size'] = 15+(15*weight/len(cluster3index))**1.2
        wordJson.append(x)
outfile = open('Results/individualCluster.html', 'w+')
outfile.write(wordCloudHTML.header())
outfile.write(json.dumps(wordJson))
outfile.write(wordCloudHTML.footer())
outfile.close()


# GEPHI EXPORT
#make data the other square
data = np.column_stack(data)

outfile = open('Results/distances.csv', 'w+')
outfile.write(';')
for ii in range(len(labels)):
    outfile.write(labels[ii])
    if ii == len(labels)-1:
        outfile.write('\r')
    else:
        outfile.write(';')
for ii in range(len(data)):

    dist = [1-scipy.spatial.distance.cosine(data[ii],datum) for datum in data]
    threshold = sorted(dist)[-4]

    for kk in range(len(dist)):
        if dist[kk] < threshold:
            dist[kk] = 0
        if kk == 0:
            outfile.write(labels[ii] + ';')
            outfile.write(str(dist[kk]) + ';')
        elif kk == len(data)-1:
            if ii != len(data)-1:
                outfile.write(str(dist[kk]) + '\r')
            else:
                outfile.write(str(dist[kk]))
        else:
            outfile.write(str(dist[kk]) + ';')
outfile.close()

