import math
import heapq
import time

from Simplify_velocity import get_velocity, label, get_split_pair
from error import Position_error, CED

def ATS(trajectory, min_gini):
    """Adaptive Trajectory Simplification
    
        Given a raw traejctory and a threshold of gini index, retuen a simplified trajectory.
        1. partition trajectory by gini index to different sub-trajectory with consistent velocity
        2. simplify each sub-trajectory adaptively by suitable position-error tolerance of threshold mapping table
        3. merge all simplified sib-trajectories to a complete simplified trajectory
            
        INPUT
            trajectory: raw trajectory
                e.g.
                [
                    {'tid': 0, 'index': 0, 'x': 10, 'y': 10.5},
                    {'tid': 0, 'index': 1, 'x': 11, 'y': 10.3},
                    {'tid': 0, 'index': 2, 'x': 15, 'y': 12.5}...
                ]
            min_gini: partition threshold
        OUTPUT
            simplified trajectory idx list
                e.g. [0, 1, 5, 9, 10]
    """
    if len(trajectory) == 0:
        return -1
    
    
    """
        partitions by avg velocity
    """
    
    partitionTime = 0
    simplificationTime = 0
    mergeTime = 0
    
    
    tStart = time.time()
    
    pair_list = get_split_pair(trajectory, min_gini)    # partition
    
    partitionTime = time.time() - tStart
    
    
    simplified_set = set()
    
    epsilon = 0
    

    threshold_mapping_table = [0.00011280332154717442, 0.0003203378645644717, 0.000488333173882603, 0.0015425776856441526] #g=0.5, alpha = 0.5

    
    
    
    """
        simplification
    """
    for idx in xrange(len(pair_list)):
    
        tStartSimplification = time.time()
        
        start = pair_list[idx][0]
        end = pair_list[idx][1]
    
        sub_trajectory = trajectory[start:end+1]
        
        velocity_list = get_velocity(sub_trajectory)
        avg_velocity = sum(velocity_list) / float(len(velocity_list))
        L = label(avg_velocity)     # get average velocity group id
        
        epsilon = threshold_mapping_table[L]  # get epsilon from threshold mapping table

        S = EBT(sub_trajectory, epsilon)    # simplify each sub-trajectory    

        S = [i+start for i in S]
        
        simplificationTime += time.time() - tStartSimplification
        
        tStartMerge = time.time()
        
        map(lambda i: simplified_set.add(i), S) # combine sub-trajectories
        
        mergeTime += time.time() - tStartMerge

    
    tStartMerge = time.time()
    
    simplified_list = list(simplified_set)
    simplified_list.sort()  # sort simplified trajectory
    
    mergeTime += time.time() - tStartMerge
    
    ## print processing time in each steps##
    # print partitionTime, simplificationTime, mergeTime
    
    return simplified_list
   
def NP_ATS(trajectory, min_gini):
    """Non-Partition Adaptive Trajectory Simplification
        
        A streaming version of ATS
        Given a raw traejctory and a threshold of gini index, retuen a simplified trajectory.
        1. add each incomming point p to buffer
        2. calculate the error of buffer and whether velocity changes
        3. keep p if error > error tolerance from threshold mapping table or velocity changes
        4. stop while adding the last point of trajectory to buffer
            
        INPUT
            trajectory: raw trajectory
                e.g.
                [
                    {'tid': 0, 'index': 0, 'x': 10, 'y': 10.5},
                    {'tid': 0, 'index': 1, 'x': 11, 'y': 10.3},
                    {'tid': 0, 'index': 2, 'x': 15, 'y': 12.5}...
                ]
            min_gini: partition threshold (useless)
        OUTPUT
            simplified trajectory idx list
                e.g. [0, 1, 5, 9, 10]
    """
    
    if len(trajectory) == 0:
        return -1


    threshold_mapping_table = [0.00011280332154717442, 0.0003203378645644717, 0.000488333173882603, 0.0015425776856441526] #g=0.5, alpha = 0.5

    
    velocity_list = get_velocity(trajectory)    # get velocity list
    
    epsilon_list = [threshold_mapping_table[label(v)] for v in velocity_list]  # get suitable epsilons for each segment from threshold_mapping_table
    
   
    S = EBT_Adaptive(trajectory, epsilon_list)  # simplify trajectory adaptively

    return S
    
def EBT(trajectory, epsilon):
    """return a simplified trajectory whoes error < epsilon
        
        INPUT
            trajectory: raw data
            epsilon: the maximun position error tolerance
        
        OUTPUT
            a simplified trajectory ids [0,1,4,7]
    """
    buffer = []
    simplified = []
    
    eud = lambda x,y: math.sqrt( pow(x['x'] - y['x'], 2) + pow(x['y'] - y['y'], 2))
    
    simplified.append(0)
    
    for idx, point in enumerate(trajectory):
        
        buffer.append(point)  # add incoming point to buffer
    
        if len(buffer) > 1:
            deviation = Position_error(0, len(buffer)-1, buffer)  # calculate error of buffer

            
            if deviation > epsilon:  # keep point if error > given epsilon
                simplified.append(idx-1)
                buffer = buffer[-2:]
    
    simplified.append(len(trajectory)-1)
    return simplified
    
def EBT_Adaptive(trajectory, epsilon_list):
    """return a simplified trajectory whoes error < epsilon_list and velocity changes
        
        INPUT
            trajectory: raw data
            epsilon_list: the maximun position error tolerance list for each segments
        
        OUTPUT
            a simplified trajectory ids [0,1,4,7]
    """
    
    buffer = []
    simplified = []
    
    WindowLength = 2
    
    eud = lambda x,y: math.sqrt( pow(x['x'] - y['x'], 2) + pow(x['y'] - y['y'], 2))
    
    simplified.append(0)  # keep the first point
    
    for idx, point in enumerate(trajectory):

        buffer.append(point)    # add incomming point to buffer
        
        if len(buffer) > 1:
            deviation = Position_error(0, len(buffer)-1, buffer)    # calculate error of buffer

            if deviation > epsilon_list[idx-1]:     # keep point if error > epsilon
                simplified.append(idx-1)
                buffer = buffer[-2:]
            elif epsilon_list[idx-1] != epsilon_list[idx-2] and epsilon_list[idx-1] == epsilon_list[min(idx, len(trajectory)-2)]:   # keep point if velocity changes
                simplified.append(idx-1)
                buffer = buffer[-2:]
            
    simplified.append(len(trajectory)-1)    # add the last point
    return simplified