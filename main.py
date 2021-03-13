import re
from nltk.corpus import stopwords

def create_doc_dict(raw):   
    # Create a dictionary of articles from the collections
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
    return collection

def get_article_wordlist(collection):
    # Create a list of words (only the ones we need) for each article, 
    for k,v in collection.items():
        k1 = 1
        l1 = []
        for i in range(len(v)):
            m = re.match('\.([A-Z])\n', v[i])
            if m:
                k1 = m.group(1)
            if k1 == 'T' or k1 == 'W' or k1 == 'A':
                if not m:
                    l1 += re.split(",|;| |:|\?|!|,|\'|\"|\.|-|\n|\t|\(|\)",v[i])     
        collection[k] = l1
    return collection

def create_article_frequency_dict(collection):
    # Create a frequency dictionary
    collectionFreq = {}
    
    stop_words = set(stopwords.words('english')) 
    
    for k,v in collection.items():
        tmpDict = {}
        for word in v:
            word = word.lower()
            if word not in stop_words and word != ' ':
                if word in tmpDict.keys():
                    tmpDict[word] += 1
                else:
                    tmpDict[word] = 1
        collectionFreq[k] = tmpDict
    return collectionFreq

def create_word_frequency_dict(collection):
    # Create a frequency dictionary
    collection_freq = {}
    
    stop_words = set(stopwords.words('english')) 

    
    for k,v in collection.items():
        
        for word in v:
            word = word.lower()
            if word not in stop_words and word != ' ':
                if word not in collection_freq.keys():
                    collection_freq[word] = {k: 1}
                else:
                    if k not in collection_freq[word].keys():
                        collection_freq[word][k] = 1
                    else:
                        collection_freq[word][k] += 1
                
    return collection_freq


    

# Reading the collection file
raw = open('.\Data\cacm.all', 'r')

raw = raw.readlines()

collection = create_doc_dict(raw)

collection = get_article_wordlist(collection)

collection_article_freq = create_article_frequency_dict(collection)

collection_word_freq = create_word_frequency_dict(collection)











































