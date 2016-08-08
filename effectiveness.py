import math
import random
def DCG(score_list):
    dcg = 0
    for idx, score in enumerate(score_list,1):
        if idx ==1:
            dcg += score
        else:
            dcg += float(score)/math.log(idx,2)
    return dcg

def AveragePrecision(relevant, retrieved):
    """Average Precision
    
        INPUT
            relevant: groundtruth
            retrieved: created result
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
            # print precision
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