



# Reading the collection file
raw = open('.\Data\cacm.all', 'r')

raw = raw.readlines()

# Create a dictionary of articles from the collections
import re

l = []
k1 = 1

collection = {}

for line in raw:
    if re.match('\.I \d+', line):
        m = re.match('\.I (\d+)', line)
        k2 = m.group(1)
        
    if k1 == k2:
        l.append(line)
    else: 
        collection[int(k1)] = l
        l = []
        k1 = k2
collection[int(k1)] = l


# Create a list of words (only the ones we need) for each article, 
for k,v in collection.items():
    
    l1 = []
    for i in range(len(v)):
        m = re.match('\.([A-Z])\n', v[i])
        if m:
            k1 = m.group(1)
        if k1 == 'T' or k1 == 'W' or k1 == 'A':
            if not m:
                l1 += re.split(",|;| |:|\?|!|,|\'|\"|\.|-|\n|\t",v[i])     
    collection[k] = l1

# Create a frequency dictionary
collectionFreq = {}

for k,v in collection.items():
    tmpDict = {}
    for word in v:
        if word in tmpDict.keys():
            tmpDict[word] += 1
        else:
            tmpDict[word] = 1
    collectionFreq[k] = tmpDict
    


















































