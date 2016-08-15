import logging
import psycopg2cffi
import argparse
import heapq
import math
import os
import json

from get_trajectory import get_from_id, get_file
from simplification.Simplify_velocity import eud, get_velocity, gini_index, label, get_label_list, split, get_split_pair
from simplification.error import CED, sum_CED, error_calculate


conn_string = "host='127.0.0.1' dbname='adsl' user='adsl' password='radsl'"
conn = psycopg2cffi.connect(conn_string)



def TrajectoryPartition(trajectory, min_gini):
    """
        Partition one trajectory into several sub-trajectories
    """
    
    ## partition trajectory
    partition_list = get_split_pair(trajectory, min_gini)
    
    sub_trajectory_list = []
    
    
    for idx in xrange(len(partition_list)):
        
        ## get sub-trajectory
        start = partition_list[idx][0]
        end = partition_list[idx][1]

        sub_trajectory_list.append(trajectory[start:end+1])
    
    return sub_trajectory_list

def ThresholdCalculation(trajectory, alpha):
    """Adaptive simplification
    
        Use a parameter alpha to calculate the best simplification result by adaptive score.
        Use sum of error insdeed of maximum of error
        
        Args:
            trajectory: Original trajectory
        Returns:
            group ID, suitable velocity
    """
    
    if len(trajectory) == 2 or len(trajectory) == 0 : return (-1,0)
        
    
    '''
        error_list
            (error*-1,(start,index,end))

        result
            simplified result
    '''
    
    result = []
    
    start = 0
    end = len(trajectory)-1
    result.append(start)
    result.append(end)

    """
        error_list
        score_list
        index_list
    """
    
    error_list = []
    score_list = []
    index_list = []
        
    
    ''' Calculate sum of error from start to end '''
    SUM_ERROR = max_error = sum_CED(trajectory, result)
    if SUM_ERROR == 0: return (-1, 0)
    
    heapq.heapify(error_list)
    heapq.heappush(error_list, error_calculate(start,end,trajectory))

    min_score = 1.0
    min_score_index = -1
    
    for i in xrange(len(trajectory)-2):
        segment = heapq.heappop(error_list)
        start = segment[2][0]
        index = segment[2][1]
        end = segment[2][2]
        seg_max_error = segment[0] * -1.  # error of this segment
        seg_sum_error = segment[1]
        
        
        left =  error_calculate(start,index,trajectory)
        right = error_calculate(index,end,trajectory)
        
        """
            To be improvement
        """
        
        SUM_ERROR = SUM_ERROR - seg_sum_error
        if left != 0:
            SUM_ERROR += left[1]
        if right != 0:
            SUM_ERROR += right[1]
        
        error = SUM_ERROR               # use sum error as error
        
        index_list.append(index)
        score = alpha * (error/max_error) + (1-alpha) * (float(len(index_list)-2)/float(len(trajectory)-2))
        score_list.append(score)
        
        
        if left != 0 :
            heapq.heappush(error_list, left )
        if right != 0 :
            heapq.heappush(error_list, right )
            
            
        if score <= min_score:          # find minimun score
            min_score = score
            min_score_index = i
        elif i - min_score_index > 5:   #stop if aware to top score
                break
   
    min_score = 1.
    idx = -1
    for (score_idx, score) in enumerate(score_list):
        if score <= min_score:
            min_score = score
            idx = score_idx
    
    result += index_list[:idx+1]
    result.sort()

    
    AV = AvgVelocity(trajectory)
    SuitableEpsilon = CED(trajectory, result)
    Label = label(AV)

    
    return (Label, SuitableEpsilon)

def AvgVelocity(trajectory):
    VelocityList = []
    for idx in xrange(len(trajectory)-1):
        start = trajectory[idx]
        end = trajectory[idx+1]
        VelocityList.append(eud(start, end))
    
    return sum(VelocityList)/len(VelocityList)
def eud(x,y):
    return math.sqrt( pow(x['x'] - y['x'], 2) + pow(x['y'] - y['y'], 2))
if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='PROG', description='Compare nDCG and hit rate of STD and DP algotithm')
    parser.add_argument('-f', '--file', default='example.txt', help = 'dataset name (default: example.txt)')
    parser.add_argument('-g', '--gini', type = float, default=0.5, help = 'gini index (default: 0.5)')
    parser.add_argument('-a', '--alpha', type = float, default=0.5, help = 'alpha (default: 0.5)')
    
    args = parser.parse_args()
    file_name = args.file
    min_gini  = args.gini
    alpha = args.alpha
    print args
    
    logging.info("retrieve dataset")
    
    raw_path = 'dataset/raw/'+file_name[0:-4] + '.txt'
    if os.path.isfile(raw_path):
        print "use saved file: " + raw_path
        raw_fin = open(raw_path,'r')
        dataset = json.loads(raw_fin.readline())
    else:
        dataset = get_file('tid_list/'+file_name)
    
    logging.info("partition")
    sub_trajectory_list = []
    for (tid, trajectory) in dataset:
        sub_trajectory_list += TrajectoryPartition(trajectory, min_gini)
        
    logging.info("threshold calculation")
    suitable_epsilon = [[],[],[],[]]        # 4 groups
    for sub_trajectory in sub_trajectory_list:
        Label, SuitableEpsilon = ThresholdCalculation(sub_trajectory, alpha)
        if Label != -1:
            suitable_epsilon[Label].append(SuitableEpsilon)
        # print Label, SuitableEpsilon
        
    logging.info("distribution analysis")
    print "groupID epsilon"
    
    epsilon_list = []
    for gid, group in enumerate(suitable_epsilon):
        avg_epsilon = sum(group)/len(group)
        print gid, avg_epsilon*111000, "m"
        epsilon_list.append(avg_epsilon)
    print epsilon_list