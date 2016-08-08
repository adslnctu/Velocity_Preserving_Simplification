import math

"""
    MAX Closet EU Distance
"""
def CED(trajectory, S):
    max_error = 0
    for start, end in [(S[idx],S[idx+1]) for idx in range(len(S)-1)]:
        max_error = max(max_error, Position_error(start,end,trajectory))
    return max_error

    
"""
    SUM Closet EU Distance
"""
def sum_CED(trajectory, S):
    error_list = []
    for start, end in [(S[idx],S[idx+1]) for idx in range(len(S)-1)]:
        for idx in xrange(start+1, end):
            point       = trajectory[idx]
            start_point = trajectory[start]
            end_point   = trajectory[end]
            error_list.append(shortestDistanceToSegment(point, start_point, end_point))
    return sum( error_list)


def SED(trajectory, S):
    max_error = 0
    for start, end in [(S[idx],S[idx+1]) for idx in range(len(S)-1)]:
        max_error = max(max_error, Direction_error(start,end,trajectory))
    return max_error

"""
    MAX velocity error!
"""
def V_ERROR(trajectory, S):
    max_error = 0
    error_list = []
    for start, end in [(S[idx],S[idx+1]) for idx in range(len(S)-1)]:
        if end > start + 1:
            V_error = velocity_error(start,end,trajectory)
            max_error = max(max_error, V_error)
            error_list.append(V_error)
        
    # return max_error
    if len(error_list) == 0: return 0
    return sum(error_list)/len(error_list)
    
def error_calculate(start,end,trajectory):
    """Calculate error from start and end point
    
    Args:
        start: Start point of trajectory
        end: End point of trajectory
        trajectory: original data
    
    Returns:
        A structure tuple, include maximun, sum of error, and start, index, end point
        example:
            (-1. * max_error, sum_error, (start, index, end))

    """
    if start >= end:
        return 0
    if end == start+1:
        return 0
    max_error = 0
    sum_error = 0
    index = -1
    
    for i in xrange(start+1, end):
        d = shortestDistanceToSegment(trajectory[i], trajectory[start], trajectory[end])
        sum_error += d
        if d > max_error:
            index = i
            max_error = d
    return (-1. * max_error, sum_error, (start, index, end))

def Position_error(start,end,trajectory):
    if start >= end:
        return -1
    if end == start+1:
        return 0
    max_error = 0
    
    for idx in range(start+1, end):
        point       = trajectory[idx]
        start_point = trajectory[start]
        end_point   = trajectory[end]
        max_error = max(max_error, shortestDistanceToSegment(point, start_point, end_point))
    return max_error
    
def Direction_error(start, end, trajectory):
    if start >= end:
        return -1
    if end == start+1:
        return 0
    max_error = 0
    main_x = trajectory[end]['x'] - trajectory[start]['x']
    main_y = trajectory[end]['y'] - trajectory[start]['y']
    main_dirction = (math.atan2(main_y, main_x) + 2*math.pi) % (2*math.pi)

    for index in range(start, end):
        x = trajectory[index+1]['x'] - trajectory[index]['x']
        y = trajectory[index+1]['y'] - trajectory[index]['y']
        direction = (math.atan2(y, x) + 2*math.pi) % (2*math.pi)
        error = min(abs(main_dirction-direction), 2*math.pi - abs(main_dirction-direction))
        max_error = max(max_error, error)
    return max_error

    
def velocity_error(start,end,trajectory):
    if start >= end:
        return 0
    if end == start+1:
        return 0
    max_error = 0
    
    eud = lambda x,y: math.sqrt( pow(x['x'] - y['x'], 2) + pow(x['y'] - y['y'], 2))
    
    time_interval = end - start
    
    ## velocity from start to end location of trajectory
    # avg_velocity = trajectory_length( start, end, trajectory) / time_interval
    avg_velocity = eud(trajectory[start], trajectory[end]) / time_interval
    for i in xrange( start, end):
        velocity = eud(trajectory[i], trajectory[i+1])
        
        if velocity != 0 and avg_velocity != 0:
            # max_error = max(max_error, abs(avg_velocity - velocity) / avg_velocity)
            max_error = max(max_error, abs(avg_velocity - velocity))
    
    return max_error



def approximate_trajectory(trajectory, S):
    approx_tra = []
    
    for i in xrange(len(S)-1):
        pre_idx = S[i]
        nex_idx = S[i+1]
        
        # print pre_idx, nex_idx
        
        seg_size = nex_idx - pre_idx
        diff_x = trajectory[nex_idx]['x'] - trajectory[pre_idx]['x']
        diff_y = trajectory[nex_idx]['y'] - trajectory[pre_idx]['y']
        
        # print seg_size, diff_x, diff_y
        
        approx_tra.append(trajectory[pre_idx])
        
        for idx in xrange(pre_idx+1, nex_idx):
            approx_x = (idx - pre_idx)/float(seg_size) * diff_x + trajectory[pre_idx]['x']
            approx_y = (idx - pre_idx)/float(seg_size) * diff_y + trajectory[pre_idx]['y']
            
            # print approx_x, approx_y
            
            approx_tra.append({'x': approx_x, 'y': approx_y})
            
    approx_tra.append(trajectory[-1])
    

    return approx_tra
        
    
def length_ratio(trajectory, S):
    min_ratio = 1.0
    
    eud = lambda x,y: math.sqrt( pow(x['x'] - y['x'], 2) + pow(x['y'] - y['y'], 2))
    
    approx_tra = approximate_trajectory(trajectory, S)
    for i in xrange(len(trajectory)-1):
        pre_idx = trajectory[i]
        nex_idx = trajectory[i+1]
        if eud(trajectory[i], trajectory[i+1]) == 0:
            continue
        diff_ratio = eud(approx_tra[i], approx_tra[i+1]) / eud(trajectory[i], trajectory[i+1])
        min_ratio = min(min_ratio, diff_ratio)
        
        print min_ratio
        
    return min_ratio
    
def shortestDistanceToSegment(point, start_point, end_point):
    eud = lambda x,y: math.sqrt( pow(x['x'] - y['x'], 2) + pow(x['y'] - y['y'], 2))
    a = end_point['y'] - start_point['y']
    b = start_point['x'] - end_point['x']
    c = -1 * b * start_point['y'] - a * start_point['x']
    # if math.sqrt(pow(a,2) + pow(b,2)) == 0: return 0
    if math.sqrt(pow(a,2) + pow(b,2)) == 0: return eud(point, start_point)
    
    return abs( a * point['x'] + b * point['y'] + c) / math.sqrt(pow(a,2) + pow(b,2))

    
"""
Calculate the length from s to e
"""
def trajectory_length(s, e, trajectory):
    length = 0
    eud = lambda x,y: math.sqrt( pow(x['x'] - y['x'], 2) + pow(x['y'] - y['y'], 2))
    for start, end in [(idx,idx+1) for idx in range(s,e)]:
        length += eud(trajectory[start], trajectory[end])
    return length
  

    