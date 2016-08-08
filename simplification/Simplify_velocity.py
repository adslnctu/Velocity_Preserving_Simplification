import math

from collections import Counter

def eud(x,y):
    """
        return lat lon distance
        INPUT
            x: firt point
            y: second point
        OUTPUT
            distance from x to y
    """
    return math.sqrt( pow(x['x'] - y['x'], 2) + pow(x['y'] - y['y'], 2))

    
def get_split_pair(trajectory, min_gini=0.5):
    """
        return the partition list (start, end) from trajectory
    """
    label_list = get_label_list(trajectory)
    split_list = [0, len(trajectory)-1]
    split(label_list, split_list, 0, min_gini)
    split_list.sort()
    pair_list = [(split_list[i],split_list[i+1]) for i in xrange(len(split_list)-1)]
    return pair_list
    

def get_velocity(trajectory):
    """
        return velocity list
        
        INPUT
            trajectory
        OUTPUT
            a list of velocity in each point
    """
    velocity_list = []
    for i in xrange(len(trajectory)-1):
        velocity_list.append(eud(trajectory[i], trajectory[i+1]))
    return velocity_list

def get_avg_velocity(trajectory):
    """
        return average velocity
        
        INPUT
            trajectory
        OUTPUT
            average velocity of trajectory
    """
    velocity_list = get_velocity(trajectory)
    return sum(velocity_list) / len(velocity_list)
    
def gini_index(velocity_list):
    l = len(velocity_list)
    if l == 0: return 0
    distribution = Counter(velocity_list).values()
    return 1-sum([pow(float(count)/l, 2) for count in distribution])
    
def label(velocity):
    """
        Convert coutinious velocity to dicrete group id
        
        INPUT
            velocity (unit: distance of lat,lon / 15 secs)
        OUTPUT
            group ID
    """
    if velocity < 0.0007277: return 0
    elif velocity < 0.001871: return 1
    elif velocity < 0.003518: return 2
    else: return 3

def get_label_list(trajectory):
    velocity_list = get_velocity(trajectory)
    return  [label(velocity) for velocity in velocity_list]

    
def split(label_list, split_list, start_point, min_gini):
    
    if gini_index(label_list) <= min_gini or len(label_list) < 3: return
    
    gini_list = [float(len(label_list[:idx]))/len(label_list)*gini_index(label_list[:idx]) \
        + float(len(label_list[idx:]))/len(label_list)*gini_index(label_list[idx:]) \
        for idx in xrange(0,len(label_list)+1)]
    
    (m,i) = min((v,i) for i,v in enumerate(gini_list))
    
    split_list.append(i+start_point)
    
    split(label_list[:i], split_list, start_point, min_gini)
    split(label_list[i:], split_list, start_point+i, min_gini)
    
    return
