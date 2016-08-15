from error import shortestDistanceToSegment

def DouglasPeuckerRecursive(trajectory, start, end, epsilon, keep_list):
    # Add START and END points
    if len(keep_list) == 0:
        keep_list += [0, len( trajectory) -1]
    if start+1 == end: return
    
    
    dmax = -1
    index = -1
    
    for i in xrange(start+1, end):
        d = shortestDistanceToSegment(trajectory[i], trajectory[start], trajectory[end])
        if d > dmax:
            index = i
            dmax = d
            
    if dmax > epsilon:
        keep_list.append(index)
        keep_list.sort()
        DouglasPeuckerRecursive(trajectory, start, index, epsilon, keep_list)
        DouglasPeuckerRecursive(trajectory, index, end, epsilon, keep_list)

def DP(trajectory, epsilon):
    """DouglasPeucker simplification
    Use DouglasPeucker to simplify trajectory, and return a list of index of trajectory
    
    Args:
        trajectory: The raw data, formate is a list of points, include tid, index, x, y.
            Example:
                [
                    {'tid': 0, 'index': 0, 'x': 10, 'y': 10.5},
                    {'tid': 0, 'index': 1, 'x': 11, 'y': 10.3},
                    {'tid': 0, 'index': 2, 'x': 15, 'y': 12.5},                
                ]
        epsilon: The minimun error can be toleranced
    
    Returns:
        A list of Simplified trajectory index.
        Example:
            [0, 1, 5, 9, 10]
    """
    keep_list = []
    DouglasPeuckerRecursive(trajectory, 0, len( trajectory)-1, epsilon, keep_list)
    return keep_list
