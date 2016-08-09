# coding=utf-8
"""
    This Process tests the velocity error, storage and effectiveness of ATS, NP-ATS, and other simplification methods.

    framwork
        1. retrieve raw dataset from tid list file
        2. simplify raw dataset by different simplifications
        3. calculate the effectiveness of each simplified dataset by testing the top-k similar trajectory retrieval
"""
import sys
import time
import random
import copy
import math
import os
import json
from prettytable import from_csv
import logging
import psycopg2cffi

logging.basicConfig(level=logging.INFO)

from get_trajectory import get_from_id, get_file

from simplification.DPTS import DPTS_approx
from simplification.IriImai import IriImai
from simplification.ATS import NP_ATS, ATS
from simplification.DouglasPeucker import DP
from simplification.error import CED, SED, V_ERROR

from similarity import dtw, lcss, edr
from effectiveness import AveragePrecision as AP, DCG



conn_string = "host='127.0.0.1' dbname='NAME' user='NAME' password='PASSWD'"
conn = psycopg2cffi.connect(conn_string)

def mean_dataset(IN):
    """traversal the input, and calculate the mean of all lists in intpus
        
        INPUT
            IN: a tructure dataset which contains some list
                e.g. {a: 0, b: 1, c: [1,2,3]}
            
        OUTPUT
            the structure dataset whose list been converted to the mean value
                e.g. {a: 0, b: 1, c: 2}
    """
    # print type(IN)
    if type(IN) == list:
        return sum(IN) / float(len(IN))
    elif type(IN) == dict:
        for key, value in IN.iteritems():
            IN[key] = mean_dataset(value)
    
    return IN

def find_top_k(query, dataset, k, task, epsilon):
    """
        find the top-k similar trajectories from query trajectory and similar measurement
        
        INPUT
            query: query trajectory
            dataset: the queried dataset to find the top k trajectories
            k: the number of retrieved similar trajectories
            task: similar measurement, include dtw, lcss and edr
            epsilon: the matching threshold of EDR and LCSS, useless for DTW
            
        OUTPUT
            top k retrieved tids and its distance from query trajectory
            e.g. [(tid_1, dist_1), (tid_2, dist_2), ...(tid_k, dist_k)]
    """
    
    top_k = []
    
    min_dist = float("inf")
    max_dist = -1 * float("inf")
    
    
    if task == 'dtw':
        for tid,Tb in dataset:

            dist= dtw(query, Tb)

            if dist < min_dist:
                top_k.append((int(tid), dist))
                top_k.sort(key = lambda x : x[1])
                top_k = top_k[0:k]

                if len( top_k)<k:
                    min_dist = float("inf")
                else:
                    min_dist = top_k[-1][1]
    elif task == 'edr':
        for tid,Tb in dataset:
            dist= edr(query, Tb, epsilon)

            if dist < min_dist:
                top_k.append((int(tid), dist))
                top_k.sort(key = lambda x : x[1])
                
                top_k = top_k[0:k]

                if len( top_k)<k:
                    min_dist = float("inf")
                else:
                    min_dist = top_k[-1][1]
    elif task == 'lcss':
        for tid,Tb in dataset:

            dist= lcss(query, Tb, epsilon)

            if dist > max_dist:
                top_k.append((int(tid), dist))
                top_k.sort(key = lambda x : x[1], reverse=True)
                top_k = top_k[0:k]

                if len( top_k)<k:
                    max_dist = -1 * float("inf")
                else:
                    max_dist = top_k[-1][1]
    return top_k

def find_result(query, dataset, result, groundtruth, maxK,  task, epsilon):
    """return the effectiveness measurement from given query and groundtruth
        INPUT
            query: query trajectory
            dataset: simplified dataset
            result: output data
            groundtruth: the top-k similar trajectories from raw dataset
            maxK: max number of k
            task: task algorithm(dtw, edr, lcss)
            epsilon: maximun length threshold of EDR and LCSS
        
        OUTPUT
            the measurement of given retrieved result and groundtruth, includes hit-rate, MAP and nDCG
    """

    tStart = time.time()
    top_k = find_top_k(query, dataset, maxK, task, epsilon)  #find top-k similar trajectories in dataset
    tEnd = time.time()
    
    approx_result = [tid for (tid,dist) in top_k]  #get top-k tids
    
    
    if len(groundtruth) == 0:
        groundtruth = approx_result     # use approx_result as groundtruth if groundtruth is empty
    
    
    k_list = [k for k in range(5,maxK+1,5)]     # built a list of ascending k by step 5
   
    result['task_time'].append(tEnd - tStart)
    
    for k in k_list:    # calculate the effectiveness from different k
        
        k_groundtruth = groundtruth[:k]
        k_approx_result = approx_result[:k]
       
        nDCG = calculate_nDCG(k_approx_result, k_groundtruth)
        hit_rate = len( set(k_groundtruth)&set(k_approx_result) )/ float(k)
        MAP = AP(k_groundtruth, k_approx_result)
        
        result['nDCG'][k].append(nDCG)
        
        result['hit_rate'][k].append(hit_rate)
        result['MAP'][k].append(MAP)
        
    return groundtruth
    
def calculate_nDCG(groundtruth, approx_result):
    """return the nDCG score from groundtrugh and approx_result
        
        INTPUT
            groundtruth: the top-k similar trajectories from raw dataset
            approx_result: the top-k similar trajectories from simplified dataset
        
        OUTPUT
            the nDCG score
    """
    approx_DCG = []
    score_list = {}
    
    ground_list = range(1,len(groundtruth)+1)
    ground_list = ground_list[::-1]
    IDCG = DCG(ground_list)
    
    for rank,tid in enumerate(groundtruth):
        score_list[tid] = len(groundtruth)-rank
        
    for tid in approx_result:
        if tid in score_list:
            approx_DCG.append(score_list[tid])
        else:
            approx_DCG.append(0)
    dcg = DCG(approx_DCG)
    return float(dcg)/IDCG
  
def simplification_epsilon(dataset, epsilon, algo, dataset_name):
    """Simplification by epsilon
        
        A general simplification framwork, parameter 'epsilon' may be a error/gini/other threshold you want
        algo is the simplification algorithm algo(raw trajectory, epsilon)
        
        INPUT
            dataset: The raw dataset
            epsilon: the maximun error tolerance for Douglas-Peucker, Iri-Imai and DPTS, and the gini index threshold for ATS
            algo: the function of simplification method
            dataset_name: the name of dataset. e.g. raw, ATS, NP-ATS...
            
        OUTPUT
            simplified dataset by given simplification method
            
    """
    dataset[dataset_name] = []
    error_list = []
    sum_error_list = []
    v_error_list = []
    
    len_raw = 0.0
    len_sim = 0.0
    
    tSimp = 0
    
    for tid, tra in dataset['raw']:
        tStart = time.time()
        s_idx = algo(tra, epsilon)
        tSimp += time.time() - tStart
        
        s_tra = [tra[i] for i in s_idx]  #simplified trajectory
        
        dataset[dataset_name].append((tid, s_tra))
        error_list.append(CED(tra, s_idx))
        # sum_error_list.append(scale_RMSE(tra, s_idx))
        v_error_list.append(V_ERROR(tra, s_idx))
        # v_error_list.append(length_ratio(tra, s_idx))
        
        len_raw += float(len(tra))
        len_sim += float(len(s_idx))

    return {
        "compression_time": tSimp,
        "error": sum(error_list) / len(error_list),
        "storage": len_sim / len_raw,
        # "sum_error": sum(sum_error_list) / len(sum_error_list),
        "v_error": (sum(v_error_list) / len(v_error_list)) * 111 / 15 * 3600
        # "v_error": (sum(v_error_list) / len(v_error_list))
    }
    

def build_groundtruth(Ta, dataset, shift_size, k):
    """build groundtruth for ideal environment. (useless now)
        Generate 10 trajectories from query as backround
        shift 10% of points as noise
        range: -10 ~ 10 m (-0.0001 ~ 0.0001)
    """
    
    shift_min = 0.
    shift_max = shift_size

    for j in xrange(k):
        new_tra = copy.deepcopy(Ta)
        shift_list = random.sample([i for i in xrange(len(Ta))], int(len(Ta)*0.1))

        for idx in shift_list:
        
            angle = random.uniform(0, 2*math.pi)
            
            shift = random.uniform(shift_min, shift_max)
            
            new_tra[idx]['x'] += math.cos(angle) * shift
            new_tra[idx]['y'] += math.sin(angle) * shift
        #print "plot","backround_"+str(j)
        #plot("backround_"+str(j), new_tra)
        
        shift_min += shift_size
        shift_max += shift_size
        
        dataset.append(((100000000+j), new_tra))
        
    # randomize the dataset order
    random.shuffle(dataset)

def find_idx_from_tid(dataset, tid):
    """
        return the position of trajectory from dataset by given tid
        
        INTPUT
            dataset: trajectory dataset
            tid: trajectory id
        
        OUTPUT
            a index of dataset and tid of dataset[index] = tid
    """
    for (idx, (tid2, tra)) in enumerate(dataset):
        if tid == tid2:
            return idx
    return -1

def output_file(OutPath, result, ArguList):
    """ Write file from given argument list of result
    
        INPUT
            OutPath: the path of output file 
            result: result data
            ArguList: what you want write
        
        OUTPUT
            write result to output file
    """
    AlgoList = result.keys()
    FoutDatasetResult = open(OutPath, 'w')
    
    FoutDatasetResult.write(' ,' + ','.join(AlgoList) + '\n')
    
    for argu in ArguList:
        FoutDatasetResult.write(argu)
        for algo in AlgoList:
            FoutDatasetResult.write(','+str(result[algo][argu]))
        FoutDatasetResult.write('\n')
    
    FoutDatasetResult.close()
    
def result_output_file(result, file_name, task, measurement_list, k_list):
    """ Write file from given argument list of result
    
        INPUT
            OutPath: the output file path
            result: result data
            Measurements: what you want write
            
        output file path: result/[file_name]_[task]_[measurement].csv
    """
    AlgoList = result.keys() # simplification algorithm list
    
    # Fout.write(' ,' + ','.join(AlgoList) + '\n')
    
    for measurement in measurement_list:
        OutPath = 'result/'+file_name[0:-4]+'_'+task+'_'+measurement+'.csv'
        Fout = open(OutPath, 'w')
        

        if measurement == 'task_time':
            Fout.write(' ,' + ','.join(AlgoList) + '\n')    # print header
            Fout.write(measurement)                         # print measurement name
            for Algo in AlgoList:
                Fout.write(','+str(result[Algo][measurement]))
        else:
            if 'raw' in AlgoList:
                AlgoList.remove('raw')                          # Not print raw information
            Fout.write(' ,' + ','.join(AlgoList) + '\n')    # print header        
            for k in k_list:
                Fout.write(str(k))
                for Algo in AlgoList:
                    Fout.write(','+str(result[Algo][measurement][k]))
                Fout.write('\n')
    
        Fout.close()
    

if __name__ == '__main__':

    """
        Prepare arguments
    """
    import argparse
    parser = argparse.ArgumentParser(prog='PROG', description='Compare nDCG and hit rate of STD and DP algotithm')

    parser.add_argument('-l', '--loop', type=int, default=100, help='the number of loops you need (default: 10)')
    parser.add_argument('-f', '--file', default='example.txt', help = 'dataset name (default: short)')
    parser.add_argument('-g', '--gini', type = float, default=0.5, help = 'gini index (default: 0.5)')
    parser.add_argument('-k', '--topk', type = int, default=30, help = 'top k candidates (default: 10)')
    parser.add_argument('--task', choices=['dtw', 'edr', 'lcss'], default = 'dtw')
    parser.add_argument('-e','--epsilon', type = float, default = '0.0003', help = 'matching threshold for edr and lcss (default: 0.0003)')
    
    args = parser.parse_args()
    file_name = args.file
    task_type = 'real' # real, ideal #
    gini  = args.gini
    k = args.topk
    loop = args.loop
    task = args.task
    epsilon = args.epsilon

    print args
    
    dataset = {}
    result = {}
    result['raw'] = {'storage':1, 'compression_time':0, 'sum_error':0, 'v_error':0}
    result['ATS'] = {} # Adaptive Trajectory Simplification
    result['NP-ATS'] = {} # Adaptive Trajectory Simplification
    result['II'] = {}
    result['DP'] = {}
    result['DPTS'] = {}
    
    
    
    path = 'dataset/'+file_name[0:-4] + '_dataset.txt'
    
    print "dataset:", path
    
    if os.path.isfile(path):
        print "use saved file: " + path
        fin = open(path,'r')
        dataset = json.loads(fin.readline())
    else:
        
        
        """Build raw dataset
            
            format:
                [
                    (tid, trajectory),
                    (tid, trajectory),
                    .....
                ]
        """
        
        
        logging.info("read dataset")
        dataset['raw'] = get_file('tid_list/'+file_name)
        
        logging.info("start simplification")

        """
            build simplified datasets from different methods
        """
        
        
        result['NP-ATS'] = simplification_epsilon(dataset, 0.4, NP_ATS, "NP-ATS")
        result['ATS'] = simplification_epsilon(dataset, 0.4, ATS, "ATS")
        
        ###SHORT###
        result['II'] = simplification_epsilon(dataset, 0.000058, IriImai, "II")
        result['DP'] = simplification_epsilon(dataset, 0.000065, DP, "DP")
        result['DPTS'] = simplification_epsilon(dataset, 0.2, DPTS_approx, "DPTS")
        
        ###MEDIUM###
        # result['II'] = simplification_epsilon(dataset, 0.000048, IriImai, "II")
        # result['DP'] = simplification_epsilon(dataset, 0.000065, DP, "DP")
        # result['DPTS'] = simplification_epsilon(dataset, 0.45, DPTS_approx, "DPTS")
        
        ###LONG###
        # result['II'] = simplification_epsilon(dataset, 0.00003, IriImai, "II")
        # result['DP'] = simplification_epsilon(dataset, 0.000085, DP, "DP")
        # result['DPTS'] = simplification_epsilon(dataset, 1.1, DPTS_approx, "DPTS")
        
        
        fout = open(path,'w')
        fout.write(json.dumps(dataset, separators=(',',':')))   # write dataset to file
        
        OutPath = 'result/'+ file_name[0:-4] + '_dataset_result' + '.csv'
        
        print "Dataset result:", OutPath
        ArguList = ['storage', 'compression_time', 'v_error']
        output_file(OutPath, result, ArguList)
        fp = open(OutPath, 'r')
        tp = from_csv(fp)
        fp.close()
        print tp
    
    
    """
        L loop task
    
    """
    Algo_list = ['raw', 'ATS', 'NP-ATS', 'II', 'DP', 'DPTS']

    measurement_list = ['task_time', 'nDCG', 'hit_rate', 'MAP']
    
    k_list = [k for k in range(5,k+1,5)]
    
    ## prepare measurement!
    for Algo in Algo_list:
        result[Algo]['nDCG'] = {}
        result[Algo]['task_time'] = []
        result[Algo]['hit_rate'] = {}
        result[Algo]['MAP'] = {}
        for k in k_list:
            result[Algo]['nDCG'][k] = []
            result[Algo]['hit_rate'][k] = []
            result[Algo]['MAP'][k] = []
    
    
    for i in range(loop):   # test LOOP times to get average result
        """
            Build query and groundtruth
        """
        
        logging.info("Loop " + str(i))
        
        query_idx = random.randint(0,len(dataset['raw'])-1)
        raw_query = dataset['raw'][query_idx][1]
        
        qeury_list = {}
        TempDataset = {}

        for Algo in Algo_list:
            TempDataset[Algo] = copy.deepcopy(dataset[Algo])
            qeury_list[Algo] = TempDataset[Algo][query_idx][1]
            del TempDataset[Algo][query_idx]
        
        if task_type == 'ideal':
            shift_size = 0.00002   # 0.00001 ~ 1 m
            groundtruth = range(100000000, 100000000+k)
            
            for Algo in Algo_list:
                build_groundtruth(qeury_list[Algo], TempDataset[Algo], shift_size, k)
            
        """
            Find top-k result
        """
        
        if task_type == 'real':
            groundtruth = []  #Use result of raw dataset as groundtruth

        for Algo in Algo_list:
            # print Algo, groundtruth
            groundtruth = find_result(qeury_list[Algo], TempDataset[Algo], result[Algo], groundtruth, k, task, epsilon)

    if loop > 0:
        result = mean_dataset(result)
        result_output_file(result, file_name, task, measurement_list, k_list)
