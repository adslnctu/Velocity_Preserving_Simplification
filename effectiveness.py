import math
import random

def DCG(score_list):
    """return the DCG score from a score list
    
        given a score list, e.g. [5,4,3,2,1], calculate the DCG by adding the score with decending weight.
        e.g. DCG([5,4,3,2,1]) = 5 + 4 / log2 + 3 / log3 + 2 / log4 + 1 / log5
        
        INPUT
            score_list: a list of scores. e.g. [5,4,3,2,1]
        OUTPUT
            the DCG score
    """
    dcg = 0
    for idx, score in enumerate(score_list,1):
        if idx ==1:
            dcg += score
        else:
            dcg += float(score)/math.log(idx,2)
    return dcg

def AveragePrecision(relevant, retrieved):
    """Average Precision
    
        Given a groundtruth and a retrieval result, calculate the average precision by different k.
    
        INPUT
            relevant: groundtruth. e.g. [a,b,c,d,e]
            retrieved: created result. e.g. [a,d,e,b,f]
        OUTPUT
            A avg precision (0~1)
    """
    
    relevant = set(relevant)
    hit = 0
    precision_list = []
    
    
    for i, result in enumerate(retrieved):
        if result in relevant:
            hit += 1
            precision = float(hit) / (i+1)
            precision_list.append(precision)
    
    if len(precision_list) == 0:
        return 0
    
    return sum(precision_list) / len(precision_list)

if __name__ == '__main__':
    r = [10,9,8,7,6,5,4,3,2,1]
    
    idcg = DCG(r)
    
    random.shuffle(r)
    
    dcg = DCG(r)
    
    
    print "DCG:", dcg
    print "nDCG:", dcg/idcg