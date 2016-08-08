import math
import heapq
import time

from Simplify_velocity import get_velocity, label, get_split_pair
from error import Position_error, CED

def ATS(trajectory, min_gini):
    """
        Adaptive Trajectory Simplification
        
        INPUT
            trajectory
            min_gini: partition threshold
        OUTPUT
            simplified trajectory idx list
    """
    if len(trajectory) == 0:
        return -1
    
    
    """
    Build partitions by avg velocity
    """
    
    partitionTime = 0
    simplificationTime = 0
    mergeTime = 0
    
    
    tStart = time.time()
    
    pair_list = get_split_pair(trajectory, min_gini)
    
    partitionTime = time.time() - tStart
    
    
    simplified_set = set()
    
    epsilon = 0
    
    # epsilon_dict = [0.004592016 / 111, 0.01176842 / 111, 0.02649389 / 111, 0.05039507 / 111] #g=0.4
    epsilon_dict = [0.003461152 / 111, 0.02017883 / 111, 0.03125521 / 111, 0.08043219 / 111] #g=0.1, MAX Final Version
    # epsilon_dict = [0.00502254864192/111, 0.0255854290033/111, 0.040629531118/111, 0.112363957637/111]  # g=0.3 max
    # epsilon_dict = [0.0129068727529/111,0.0336671793759/111,0.0587065427654/111,0.16344623299/111]  # g=0.5 max
    # epsilon_dict = [0.0395070706597/111,0.0868617737273/111,0.220840329515/111,0.224195931453/111]  # g=0.7 max
    # epsilon_dict = [0.0494846202161/111, 0.0942020880901/111, 0.252738388544/111, 0.347107672303/111]  # g=0.9 max
    
    
    
    
    for idx in xrange(len(pair_list)):
    
        tStartSimplification = time.time()
        
        start = pair_list[idx][0]
        end = pair_list[idx][1]
    
        sub_trajectory = trajectory[start:end+1]
        
        velocity_list = get_velocity(sub_trajectory)
        avg_velocity = sum(velocity_list) / float(len(velocity_list))
        L = label(avg_velocity)
        
        epsilon = epsilon_dict[L]
            
 
        # S = DP(sub_trajectory, epsilon)        
        S = EBT(sub_trajectory, epsilon)        

        S = [i+start for i in S]
        
        simplificationTime += time.time() - tStartSimplification
        
        tStartMerge = time.time()
        
        map(lambda i: simplified_set.add(i), S)
        
        mergeTime += time.time() - tStartMerge

    
    tStartMerge = time.time()
    
    simplified_list = list(simplified_set)
    simplified_list.sort()
    
    mergeTime += time.time() - tStartMerge
    
    ## print processing time in each steps##
    # print partitionTime, simplificationTime, mergeTime
    
    return simplified_list
   
def NP_ATS(trajectory, min_gini):
    """
        Non-Partition Adaptive Trajectory Simplification
        
        INPUT
            trajectory
            min_gini: partition threshold (not used)
        OUTPUT
            simplified trajectory idx list
    """
    
    if len(trajectory) == 0:
        return -1
    
    
    """
    Build partitions by avg velocity
    """


    # epsilon_dict = [0.004592016 / 111, 0.01176842 / 111, 0.02649389 / 111, 0.05039507 / 111] #g=0.4
    epsilon_dict = [0.003461152 / 111, 0.02017883 / 111, 0.03125521 / 111, 0.08043219 / 111] #g=0.1, MAX Final Version
    # epsilon_dict = [0.00502254864192/111, 0.0255854290033/111, 0.040629531118/111, 0.112363957637/111]  # g=0.3 max
    # epsilon_dict = [0.0129068727529/111,0.0336671793759/111,0.0587065427654/111,0.16344623299/111]  # g=0.5 max
    # epsilon_dict = [0.0395070706597/111,0.0868617737273/111,0.220840329515/111,0.224195931453/111]  # g=0.7 max
    # epsilon_dict = [0.0494846202161/111, 0.0942020880901/111, 0.252738388544/111, 0.347107672303/111]  # g=0.9 max
    
    velocity_list = get_velocity(trajectory)
    
    epsilon_list = [epsilon_dict[label(v)] for v in velocity_list]
    
    # print [label(v) for v in velocity_list]
    # print epsilon_list
    
    S = EBT_Adaptive(trajectory, epsilon_list)

    return S
    
def EBT(trajectory, epsilon):
    buffer = []
    simplified = []
    
    eud = lambda x,y: math.sqrt( pow(x['x'] - y['x'], 2) + pow(x['y'] - y['y'], 2))
    
    simplified.append(0)
    
    for idx, point in enumerate(trajectory):
        #start point = buffer[0]
        #end point = point
        
        buffer.append(point)
    
        # print point
    
        if len(buffer) > 1:
            deviation = Position_error(0, len(buffer)-1, buffer)
            # print idx, deviation
            
            # print deviation
            
            if deviation > epsilon:
                # print idx-1
                simplified.append(idx-1)
                buffer = buffer[-2:]
    
    simplified.append(len(trajectory)-1)
    return simplified
    
def EBT_Adaptive(trajectory, epsilon_list):
    """
        Add velocity changed window
        to avoid velocity changed temporarily and restored
        e.g. 11111211111
    """
    buffer = []
    simplified = []
    
    WindowLength = 2
    
    # vThreshold = int(len(trajectory) * 0.09)
    
    eud = lambda x,y: math.sqrt( pow(x['x'] - y['x'], 2) + pow(x['y'] - y['y'], 2))
    
    simplified.append(0)
    
    for idx, point in enumerate(trajectory):

        buffer.append(point)
        if len(buffer) > 1:
            deviation = Position_error(0, len(buffer)-1, buffer)

            if deviation > epsilon_list[idx-1]:
                simplified.append(idx-1)
                buffer = buffer[-2:]
            # elif epsilon_list[idx-1] != epsilon_list[idx-2]:  # No keep
            elif epsilon_list[idx-1] != epsilon_list[idx-2] and epsilon_list[idx-1] == epsilon_list[min(idx, len(trajectory)-2)]:
                simplified.append(idx-1)
                buffer = buffer[-2:]
            
    simplified.append(len(trajectory)-1)
    return simplified