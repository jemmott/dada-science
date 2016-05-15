# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 14:02:41 2014
CWJ for Embarke
"""

import numpy as np
import scipy.spatial
import pylab as pl
import operator
import embarke
import random
import groups
import string  
import embarke_constants
import json 

# TO DO: add subject lines for each cluster

def main():
     
    # input parameters
    num_files = 100
    appId = '43b8b536-08c0-4089-9140-8a0cc5123f94' # WOS
    metric = 'cosine' # distance metric options 'euclidean' and 'cosine'
    N_tries = 5
    
    # load and format the data
    profiles = embarke.load_jsons(num_files, appId)
    campaignIds = embarke.listCampaignIds(profiles)

    data = []
    profileIds = []
    for jj in range(len(profiles)):
        profile = profiles[jj]
        clickCampaignIds = profileClickCampaigns(profile)
        x = []
        for ii in range(len(campaignIds)):
            if campaignIds[ii] in clickCampaignIds:
                x.append(1)
            else:
                x.append(0)
        # throw out the all zero cases        
        if sum(x) != 0:
            data.append(x)
            profileIds.append(profile['profileId'])
    

    # choose the best value of k
    #k = chooseK(data)
    k = 10

    # make the clusters
    clusters = makeClusters(data, k, metric, N_tries)
    
    # Find groups that characterize clusters
    profiles = groups.labelClusters(profiles, clusters, profileIds)    
    profiles = groups.make_profile_groups(profiles)
    
    for ii in range(k):   
        group_name = ("Cluster " + str(ii))
        groups_count = embarke.analyze_group(profiles, group_name)
        groupSort = sorted(groups_count.items(), key = embarke.get_surprise)
        groupSort = [x for x in groupSort if x[1]['category'] != 'clusters']  
        plotClusterSurprise(groupSort,ii, appId)

    
    
    # Find top subject lines for each cluster
    allWordWeights = wordWeights(profiles, campaignIds)
    for ii in range(k):
        cluster = clusters[ii]
        cluster['campaignIds'] = campaignIds
        campaignIdSort = [x for (y,x) in sorted(zip(cluster['center'],campaignIds), reverse = True)]    
        centerSort = sorted(cluster['center'], reverse = True)    
        
        subjects = []
        weights = []
        for jj in range(len(centerSort)):
            subject = embarke.getSubjectLine(profiles, campaignIdSort[jj])
            if subject and centerSort[jj] > 0:
                subjects.append(subject)
                weights.append(centerSort[jj])
        wordList = wordFrequency(subjects, weights)
        wordSurprise = getWordSurprise(wordList, allWordWeights)
        plotWordFrequency(wordSurprise, ii, appId)
        wordCloudExport(wordSurprise, ii, appId)
    
    gephiExport(data, appId)
    plotClusters(data, clusters, appId)
    
    return None
    
def makeClusters(data, k, metric = 'cosine', N_tries = 1):
    meanDistanceBest = 100
    # Calling the functions that do the math
    # clusters = initalizeForgy(data, k, metric)  
    for ii in range(N_tries):
        clusters = initalizeRandomPartition(data, k)
        clusters = refineClusters(data, clusters, metric)
        meanDistance = getMeanDistance(clusters, data)
        if meanDistance < meanDistanceBest:
            meanDistanceBest = meanDistance
            clustersBest = clusters    
    clusters = clustersBest
    
    return clusters


# formatting the data during initial loading
def profileClickCampaigns(profile):
    clickCampaignIds = []
    for message in profile['messages']:
        if 'clickTimes' in message.keys():
            clickCampaignIds.append(message['campaignId'])
    return clickCampaignIds
    
def profileOpenCampaigns(profile):
    openCampaignIds = []
    for message in profile['messages']:
        if 'openTimes' in message.keys():
            openCampaignIds.append(message['campaignId'])
    return openCampaignIds


# Forgy Initalization #########################################################
def initalizeForgy(data, k, metric):

    # defining the initial cluster centers, using Forgy random method
    clusters = []
    for ii in range(k):
        cluster = {}        
        cluster['center'] = data[ii]
        cluster['members'] = [ii]
        clusters.append(cluster)
        
    # step through all of the data in order, adding to the nearest cluster center
    for ii in range(len(data)):
        # find distances from current point to cluster centers
        distances = getDistances(clusters,data[ii], metric)
        # add the point to the nearest cluster
        min_index, min_value = min(enumerate(distances), key=operator.itemgetter(1))
        if ii not in clusters[min_index]['members']:
            clusters[min_index]['members'].append(ii)
        
        # recalculate cluster center
        clusters = clusterCenters(clusters, data)

    return clusters

    
# Random Partition Initalization ##############################################
def initalizeRandomPartition(data, k):
    clusters = []
    for ii in range(k):
        cluster = {}
        cluster['members'] = []
        cluster['center'] = []
        clusters.append(cluster)
    for ii in range(len(data)):
        rand_index = random.sample(range(k),1)[0]
        clusters[rand_index]['members'].append(ii)
    clusters = clusterCenters(clusters, data)
        
        
    return clusters
    
# step through the data again, checking to make sure that each point is 
# assigned to the closest center
def refineClusters(data, clusters, metric):
    isMoving = True
    num_iterations = 0
    max_iterations = 100
    
    while isMoving and num_iterations < max_iterations:
        isMoving = False
        for ii in range(len(data)):
            distances = getDistances(clusters, data[ii], metric)
            min_index, min_value = min(enumerate(distances), 
                                       key=operator.itemgetter(1))
            if ii not in clusters[min_index]['members']:
                # remove the index from the other cluster
                for cluster in clusters:
                    cluster['members'] = [x for x in cluster['members'] if x != ii]
                # add it to the better one
                clusters[min_index]['members'].append(ii)
                clusters = clusterCenters(clusters, data)
                isMoving = True

        num_iterations = num_iterations + 1
        if num_iterations == 100:
            print('Maximum number of cluster refining iterations reached.')
    return clusters
    
# reclaculates the cluster centeres based on its memebership
def clusterCenters(clusters, data):
    for ii in range(len(clusters)):
        cluster_data = getData(clusters[ii], data)
        clusters[ii]['center'] = np.mean(cluster_data,axis=0)
    return clusters
    
# find the distances from a data point to all of the cluster centers
def getDistances(clusters, datum, metric = 'cosine'):
    if metric == 'cosine':
        distances = [scipy.spatial.distance.cosine(datum,cluster['center']) 
                    for cluster in clusters]
    if metric == 'euclidean':
        distances = [scipy.spatial.distance.euclidean(datum,cluster['center']) 
                    for cluster in clusters]
        
    return distances
    
def getMeanDistance(clusters, data):
    distance = 0    
    for cluster in clusters:
        distance = distance + np.mean([scipy.spatial.distance.euclidean(data[index],cluster['center']) 
                    for index in cluster['members']])
    distance = distance / len(clusters)
    return distance
    
    
# choosing the best value of K using the Silhouette method
def chooseK(data):
    kRange = range(5,20)
    metric = 'cosine'
    N_tries = 3
    silhouette = []
    for k in kRange:
        clusters = makeClusters(data, k, metric, N_tries)
        silhouette.append(get_silhouette(clusters, data))
    print(silhouette)
    bestK = kRange[silhouette.index(max(silhouette))]
    print("Best k is " + str(bestK))
    return bestK

def get_silhouette(clusters, data):
    s = []
    for ii in range(len(data)):
        b = 1
        for cluster in clusters:
            if ii in cluster['members']:
                a = np.mean([scipy.spatial.distance.cosine(data[ii],data[jj])
                        for jj in cluster['members'] if jj != ii])
            else:
                b_clust = np.min([scipy.spatial.distance.cosine(data[ii],data[jj])
                        for jj in cluster['members']])
                b = np.min([b,b_clust])
        s.append((b-a)/np.max([a,b]))
    silhouette = np.mean(s)
    return silhouette
   
   
# pull all of the data points that are assigned to a certain cluster
def getData(cluster, data):
    cluster_data = np.vstack([data[x] for x in cluster['members']])
    return cluster_data
    
# get the values of the cluster centers from the custers list
def getCenters(clusters):
    centers = np.vstack([x['center'] for x in clusters])
    return centers
    
# get the values of a cluster center from the cluster
def getCenter(cluster):
    center = cluster['center']
    return center

# get the list of members of each cluster from the clusters list
def getClusters(clusters, data):
    cluster_list = -np.ones(len(data))
    for ii in range(len(clusters)):
        for index in clusters[ii]['members']:
            cluster_list[index] = ii
    cluster_list = list(cluster_list)
    return cluster_list

# Word frequency from subject lines
def wordFrequency(subjects, weights):
    commonWords = embarke_constants.commonWords
    
    wordList = {}
    for ii in range(len(subjects)):
        subject = subjects[ii]
        # format the text
        subject = subject.translate(string.maketrans("",""),string.punctuation)
        subject = subject.translate(string.maketrans("",""),string.digits)
        subject = subject.title()
        words = subject.split()
        for word in words:
            if word.lower() not in commonWords:
                if len(word) > 2:
                    if word not in wordList.keys():
                        wordList[word] = weights[ii]
                    else:
                        wordList[word] = wordList[word] + weights[ii]
    return wordList
    
def wordWeights(profiles, campaignIds):
    clickRate = embarke.clickRateCampaign(profiles, campaignIds)
    subjects = []
    weights = []
    for campaignId in campaignIds:
        subject = embarke.getSubjectLine(profiles, campaignId)
        if subject:
            subjects.append(subject)
            weights.append(clickRate[campaignId])
    allSubjectWeights = wordFrequency(subjects, weights)
    return allSubjectWeights    
    
def getWordSurprise(wordList, allWordWeights):
    wordSurprise = {}
    for word in wordList.keys():
        # extra 0.001 is to deal with divide by zero problems
        numerator = wordList[word] + 0.001
        denominator = allWordWeights[word] + 0.001
        wordSurprise[word] = np.log10(10*numerator/denominator)-1
    return wordSurprise


# Data Exporting ##############################################################
# export for word cloud with d3.js
def wordCloudExport(wordSurprise, clusterNumber, appId):
    wordJson = []
    for word in wordSurprise.keys():
        x = {}
        x['text'] = word
        x['size'] = 18+120*wordSurprise[word]**2
        wordJson.append(x)
    import wordCloudHTML
    outfile = open('Results/' + appId + '/cluster' + str(clusterNumber) + '.html', 'w+')
    outfile.write(wordCloudHTML.header())
    outfile.write(json.dumps(wordJson))
    outfile.write(wordCloudHTML.footer())

    return None

def gephiExport(data, appId):
    outfile = open('Results/' + appId + '/distances.csv', 'w+')
    outfile.write(';')
    for ii in range(len(data)):
        outfile.write(str(ii))
        if ii == len(data)-1:
                outfile.write('\r')
        else:
            outfile.write(';')
    for ii in range(len(data)):
        for jj in range(len(data)):
            # 1-distance for affinity
            dist = 1-scipy.spatial.distance.cosine(data[ii],data[jj])
            # This makes an "r neighborhood" graph
            r = 0.5
            if dist < r:
                dist = 0
            if jj == 0:
                outfile.write(str(ii) + ';')
                outfile.write(str(dist) + ';')
            elif jj == len(data)-1:
                if ii != len(data)-1:
                    outfile.write(str(dist) + '\r')
                else:
                    outfile.write(str(dist))
            else:
                outfile.write(str(dist) + ';')
    
    return None

# plotting ####################################################################
def plotClusters(data, clusters, appId):
    centers = getCenters(clusters)
    
    pl.figure()
    pl.pcolor(centers, cmap="binary")
    pl.savefig('Results/' + appId + '/ClusterResults.png')
    pl.close('all')

    return None

def plotClusterSurprise(groupSort, clusterNumber, appId):
    names = []
    surprise = []
    for x in groupSort:
        if 'surprise' in x[1].keys():
            names.append(x[0])
            surprise.append(x[1]['surprise'])
    surprise = [np.sign(s)*min(abs(s),0.5) for s in surprise]
    
    fig = pl.figure()
    ax = fig.add_subplot(111)
    ax.barh(range(len(names)),surprise, align='center')
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names)
    ax.set_xticks([-0.5, 0, 0.5])
    ax.set_xticklabels(['Less Common', 'Same', 'More Common'])
    fig.subplots_adjust(left=0.3)
    
    ax.axvline(0,color='k',lw=3)   # poor man's zero level
    
    ax.set_xlabel('Performance')
    ax.set_title('How is cluster ' + str(clusterNumber) + ' different?')
    pl.tight_layout()
    pl.savefig('Results/' + appId + '/Cluster' + str(clusterNumber) +
            'Results.png')
    pl.close('all')
    
def plotWordFrequency(wordList, clusterNumber, appId):
    num_words = 30
    words = sorted(wordList, key=wordList.__getitem__)[-num_words:-1]
    weights = sorted(wordList.values())[-num_words:-1]
    

    fig = pl.figure()
    ax = fig.add_subplot(111)
    ax.barh(range(len(words)),weights, align='center')
    ax.set_yticks(range(len(words)))
    ax.set_yticklabels(words)
    ax.set_xticks([0, 0.5])
    ax.set_xticklabels(['Less Common', 'More Common'])
    fig.subplots_adjust(left=0.3)
        
    ax.set_xlabel('Performance')
    ax.set_title('Subject Line Words for Cluster ' + str(clusterNumber))
    pl.tight_layout()
    pl.savefig('Results/' + appId + '/Cluster' + str(clusterNumber) +
            'Words.png')
    pl.close('all')
    
    return None


# Standard boilerplate to call the main() function.
if __name__ == '__main__':
  main()
