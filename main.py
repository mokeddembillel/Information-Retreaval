import re
import numpy as np
import nltk
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

def get_queries(path='Data/query.txt'):
    # Get and preprocess queries from the test file
    stop_words = set(stopwords.words('english')) 
    raw = open(path, 'r')
    raw = raw.readlines()
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
    for k,v in collection.items():
        l1 = []
        for i in range(len(v)):
            m = re.match('\.([A-Z])\n', v[i])
            if m:
                k1 = m.group(1)
            if k1 == 'W' or k1 == 'N':
                if not m:
                    l1 += re.split(",|;| |:|\?|!|,|\'|\"|\.|-|\n|\t|\(|\)",v[i])     
        l3=[]
        for word in l1:
            if word not in stop_words and word != '':
                l3.append(word)  
        collection[k] = l3
    return collection  

def get_queries_results(path='Data/qrels.txt'):
    # Get queries test results
    raw = open(path, 'r')
    raw = raw.readlines()
    index_query = '01'
    references={}
    l=[]
    for line in raw:
        liste = line.split()
        if liste[0] != index_query:
            references[index_query]=l
            l=[]
            index_query=liste[0]
        l.append(liste[1])
    references[liste[0]]=l
    return references

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
    # Create an article's frequency dictionary
    collectionFreq = {}
    stop_words = set(stopwords.words('english'))    
    for k,v in collection.items():
        tmpDict = {}
        for word in v:
            word = word.lower()
            if word not in stop_words:
                if word in tmpDict.keys():
                    tmpDict[word] += 1
                else:
                    tmpDict[word] = 1
        collectionFreq[k] = tmpDict
    return collectionFreq

def create_word_frequency_dict(collection):
    # Create a word's frequency dictionary (inverse file)
    collection_freq = {}
    stop_words = set(stopwords.words('english')) 
    for k,v in collection.items():    
        for word in v:
            word = word.lower()
            if word not in stop_words:
                if word not in collection_freq.keys():
                    collection_freq[word] = {k: 1}
                else:
                    if k not in collection_freq[word].keys():
                        collection_freq[word][k] = 1
                    else:
                        collection_freq[word][k] += 1            
    return collection_freq

def create_article_weights_dict(collection_article_freq, collection_word_freq):
    # Get the weights of words in each article
    max_freq={}
    weights={}
    
    for i in collection_article_freq.keys():
        max_freq[i]=max(collection_article_freq[i].values())
    
    for i in collection_article_freq.keys() :
        document_weights={}
        for j in collection_article_freq[i].keys():
            document_weights[j] = (float(collection_article_freq[i][j] / max_freq[i]) * np.log10( float(len(collection_article_freq)) / len(collection_word_freq[j].keys()) + 1))  
        weights[i] = document_weights
    return weights

def create_word_weights_dict(collection_word_freq, weights):
    # Create a word's weights dictionary (inverse file)
    collection_word_weights = collection_word_freq.copy()
    for word in collection_word_weights.keys():
        for article in collection_word_weights[word].keys():
            collection_word_weights[word][article] = weights[article][word]
    return collection_word_weights

def boolean_model(query, collection_article_freq):  
    # Boolean model
    result = []
    for article in collection_article_freq: 
        document = {}
        query_str = ''
        for word in collection_article_freq[article]:
            document[word] = collection_article_freq[article][word]
        query_words = nltk.tokenize.word_tokenize(query)    
        for word in query_words:            
            
            if(word.lower() not in ['and','or','(',')','not']): 
                if(word.lower() not in  document):
                    query_words[query_words.collection_article_freq(word)] = 0
                else:
                    query_words[query_words.collection_article_freq(word)] = 1
        for i in query_words:
            query_str = query_str+' '+str(i)
        if(eval(query_str) == 1):
            result.append(article)  
    return result 

def vector_model(query, collection_article_weights, measure):
    # A vector model that uses four measures InnerProduct, Coeff Dice, Cosinus and Jaccard
    relevent_articles = {}
    query = query.lower().split()
    if(measure == 'InnerProduct'):
        for article in collection_article_weights.keys():
            sum_ = 0
            for word in query:
                if word in collection_article_weights[article].keys():
                    sum_ += collection_article_weights[article][word]
            if(sum_ != 0):
                relevent_articles[article] = sum_         
    elif (measure == 'Coeff Dice'):
        for article in collection_article_weights.keys():
            numerator = 0
            denominator = 0
            for word in query:
                if word in collection_article_weights[article].keys():
                    numerator += collection_article_weights[article][word]
                    # Supposed to be x**2 but since the querry is binary it would be 1**2 
                    denominator += 1
            numerator *= 2
            for weight in collection_article_weights[article].values():
                denominator += weight ** 2
            dice_coef = 0
            if denominator != 0:
                dice_coef = numerator / denominator
            if(dice_coef != 0):
                relevent_articles[article] = dice_coef 
    elif (measure == 'Cosinus'):
        for article in collection_article_weights.keys():
            numerator = 0
            denominator = 0
            for word in query:
                if word in collection_article_weights[article].keys():
                    numerator += collection_article_weights[article][word]
                    # Supposed to be x**2 but since the querry is binary it would be 1**2 
                    denominator += 1
            weights_sum = 0
            for weight in collection_article_weights[article].values():
                weights_sum += weight ** 2
            denominator = np.sqrt(denominator * weights_sum)
            cosinus = 0
            if denominator != 0:
                cosinus = numerator / denominator
            if(cosinus != 0):
                relevent_articles[article] = cosinus 
    elif (measure == 'Jaccard'):
        for article in collection_article_weights.keys():
            numerator = 0
            denominator = 0
            for word in query:
                if word in collection_article_weights[article].keys():
                    numerator += collection_article_weights[article][word]
                    # Supposed to be x**2 but since the querry is binary it would be 1**2 
                    denominator += 1
            for weight in collection_article_weights[article].values():
                denominator += weight ** 2
            denominator -= numerator
            jaccard = 0
            if denominator != 0:
                jaccard = numerator / denominator
            if(jaccard != 0):
                relevent_articles[article] = jaccard 
    relevent_articles = sorted(relevent_articles.items(), key=lambda item: item[1], reverse=True)
    return relevent_articles[:100]

def recall(resultat,reference):  
    inter=[]
    for i in resultat:
        if i in reference:
            inter.append(i)
    if(len(reference)!=0):
        Rappel=(len(inter)/len(reference))
    return Rappel

# Reading the collection file
raw = open('.\Data\cacm.all', 'r')

raw = raw.readlines()

collection = create_doc_dict(raw)

collection = get_article_wordlist(collection)

collection_article_freq = create_article_frequency_dict(collection)

collection_word_freq = create_word_frequency_dict(collection)

collection_article_weights = create_article_weights_dict(collection_article_freq, collection_word_freq)

collection_word_weights = create_word_weights_dict(collection_word_freq, collection_article_weights)

# query = 'Preliminary International Algebraic Report Perlis Samelson'

# Evaluation phase

queries = get_queries()

queries_results = get_queries_results()

measures = ['InnerProduct', 'Coeff Dice', 'Cosinus', 'Jaccard']

relevent_articles = vector_model(' '.join(queries[2]), collection_article_weights, measures[0])









