



# Reading the collection file
raw = open('.\Data\cacm.all', 'r')

raw = raw.readlines()

# create a dictionary of articles from the collections
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

print(collection)




























































