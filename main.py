import re
import numpy as np
import nltk
from nltk.corpus import stopwords
import time
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
    index_query = 1
    references={}
    l=[]
    for line in raw:
        liste = line.split()
        if int(liste[0]) != index_query:
            references[index_query] = l
            l = []
            index_query = int(liste[0])
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

def word_search(dict_,word):
    return dict_[word]

def article_search(dict_, article):
    return dict_[article]

def save_dict(file_name, dict_):
    file = open(file_name,'w')
    file.write(str(dict_))
    file.close()
    

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
                    query_words[query_words.index(word)] = 0
                else:
                    query_words[query_words.index(word)] = 1
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
    return relevent_articles

def get_recall(resultat,reference):  
    inter = []
    for i in resultat:
        if str(i[0]) in reference:
            inter.append(i)
    if(len(reference)!=0):
        Rappel = (len(inter)/len(reference))
    return Rappel

def get_precision(resultat,reference):
    inter=[]
    for i in resultat:
        if str(i[0]) in reference:
            inter.append(i)
    precision = 0
    if(len(resultat) != 0):
        precision = len(inter)/len(resultat)
    else:
        print("Aucun document n'a été retourné")
    return precision

def get_f1_score(relevent_articles, query_result):
    recall = recall = get_recall(relevent_articles, query_result)
    precision = get_precision(relevent_articles, query_result)
    if recall + precision == 0:
        return 0
    return (2 * recall * precision) / (recall + precision)

# def hyper_parameter_tuning(queries, queries_results, measure):
#     best_performances = []
#     for query_number in queries:
#         if query_number not in queries_results.keys():
#                 continue
#         relevent_articles = vector_model(' '.join(queries[query_number]), collection_article_weights, measures[2])
#         best_f1_score = (0, 0, query_number)
#         for i in range(1, len(relevent_articles)):
#             f1_score = get_f1_score(relevent_articles[:i], queries_results[query_number])
#             if f1_score > best_f1_score[0]:
#                 best_f1_score = (f1_score, i, len(queries_results[query_number]))
#         best_performances.append(best_f1_score)
#         #print(best_performances[-1][0], ' -- ', best_performances[-1][1], ' -- ', len(queries[best_performances[-1][2]]))
#     return best_performances

def hyper_parameter_tuning(queries, queries_results, measure):
    # hyper
    recall = []
    precision = []
    for i in range(1, 2):
        recall_tmp = []
        precision_tmp = []
        for query_number in queries:
            if query_number not in queries_results.keys():
                continue
            relevent_articles = vector_model(' '.join(queries[query_number]), collection_article_weights, measures[2])
            max_length = len(relevent_articles)
            if i < max_length:
                max_length = i
            recall_tmp.append(get_recall(relevent_articles[:i], queries_results[query_number]))
            precision_tmp.append(get_precision(relevent_articles[:i], queries_results[query_number]))
        
        recall.append(np.mean(recall_tmp))
        precision.append(np.mean(precision_tmp))
        save_dict('recall', recall)
        save_dict('precision', precision)
    return recall, precision

def test_measures(query, query_result, measures):
    results = {}
    for measure in measures:
        t1 = time.perf_counter()
        relevent_articles = vector_model(' '.join(query), collection_article_weights, measure)
        print(relevent_articles[:11])
        recall = get_recall(relevent_articles[:11], query_result)
        precision = get_precision(relevent_articles[:11], query_result)
        t2=time.perf_counter()
        results[measure] = (recall, precision, t2 - t1)
    return results

# Reading the collection file
t1 = time.perf_counter()
raw = open('.\Data\cacm.all', 'r')

raw = raw.readlines()

collection = create_doc_dict(raw)

collection = get_article_wordlist(collection)
t2=time.perf_counter()
print("le temps d'execution de la phase d'extraction des mots clés est:", t2 - t1)

collection_article_freq = create_article_frequency_dict(collection)

t1 = time.perf_counter()
collection_word_freq = create_word_frequency_dict(collection)
t2=time.perf_counter()
print("le temps d'execution de la phase de la création de fichier inverse de fréquence est:", t2 - t1)

collection_article_weights = create_article_weights_dict(collection_article_freq, collection_word_freq)

t1 = time.perf_counter()
collection_word_weights = create_word_weights_dict(collection_word_freq, collection_article_weights)
t2=time.perf_counter()
print("le temps d'execution de la phase de la création de fichier inverse de poinds est:", t2 - t1)

# query = 'Preliminary International Algebraic Report Perlis Samelson'

# Evaluation phase
t1 = time.perf_counter()
measures = ['InnerProduct', 'Coeff Dice', 'Cosinus', 'Jaccard']

queries = get_queries()

queries_results = get_queries_results()
t2=time.perf_counter()
print("le temps d'execution de la phase d'extraction des requets est:", t2 - t1)


save_dict('collection_word_freq', collection_word_freq)

save_dict('collection_word_weights', collection_word_weights)

# relevent_articles = vector_model(' '.join(queries[1]), collection_article_weights, measures[2])

# f1_score = get_f1_score(relevent_articles, queries_results[1])

#recall, precision = hyper_parameter_tuning(queries, queries_results, measures)

# f1_score = np.divide(np.multiply(np.multiply(2, recall), precision), np.add(recall, precision))




# q = 22
# results = test_measures(queries[q], queries_results[q], measures)

# for query_number in queries:
#     if query_number not in queries_results.keys():
#         continue
#     results = test_measures(queries[query_number], queries_results[query_number], measures)
#     print(results.items())
#     print()
#     print(query_number)


print("Recherche")
print("1-rechercher par mot")
print("2-rechercher par document ")
resp=int(input())

if resp==1:
    print("Que voulez vous afficher")
    print("1-La frequence du mots dans les documents")
    print("2-Le poids du mots dans les documents")
    resp=int(input())
    if resp==1:
        print("donner le mot a rechercher")
        mot=input()
        mot=str(mot)
        print(word_search(collection_word_freq,mot))
    if resp==2:
        print("donner le mot a rechercher")
        mot=input()
        mot=str(mot)
        print(word_search(collection_word_weights,mot))
if resp==2:
    print("Que voulez vous afficher")
    print("1-La frequence des mots du document")
    print("2-Le poids des mots du document")
    resp=int(input())
    if resp==1:
        print("donner le numero de document a rechercher")
        mot=input()
        mot=int(mot)
        print(article_search(collection_article_freq,mot))
    if resp==2:
        print("donner le numero de document a rechercher")
        mot=input()
        mot=int(mot)
        print(article_search(collection_article_weights,mot))

print()
print("Modele Booleen")
print("veuillez saisir votr requete booleenne")
req=input()
req=str(req)
result=boolean_model(req, collection_article_freq)
print(result)

print()
print("Modele Vectoriel")

print("Introduire le numero de requete que vous voullez essayer ")
print(" de 1 à 64 \n")
index=input()
index=int(index)
print('\n Les mots cles de la requete sont :\n',queries[index])
print()
print('Les documents qui doivent etre trouvés :\n',queries_results[index])

print('quelle mesure du modele vectoriel voulez vous utiliser :joy:')
print('1-InnerProduct ')
print('2-Coeff Dice ')
print('3-Cosinus ')
print('4-Jaccard ')
resp=int(input())
if resp==1 :
    relevent_articles = vector_model(' '.join(queries[index]), collection_article_weights, measures[0])
if resp==2 :
    relevent_articles = vector_model(' '.join(queries[index]), collection_article_weights, measures[1])
if resp==3 :
    relevent_articles = vector_model(' '.join(queries[index]), collection_article_weights, measures[2])
if resp==4 :
    relevent_articles = vector_model(' '.join(queries[index]), collection_article_weights, measures[3])

recall = get_recall(relevent_articles[:11], queries_results[index])
print('Rappel : ', recall)
precision = get_precision(relevent_articles[:11], queries_results[index])
print('Precision : ', precision)

