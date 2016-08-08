import numpy as np
import heapq

from error import Direction_error

def DPTS_approx(trajectory, threshold):
    """Fast version
        Given the raw trajectory and direction error threshold,
        return a simplified trajectory idx (not point) with direction error < threshold
        
        INPUT
            trajectory
            threshold: maximun direction deviation
        OUTPUT
            simplified trajectory idx list [0,1,5,8]
    """
    T = [trajectory[0]]
    S = [0]
    e=0
    h=2
    n = len(trajectory)
    while h < n:
        while h < n and Direction_error(e,h,trajectory) <= threshold:
            h+=1
        T.append(trajectory[h-1])
        S.append(h-1)
        e = h-1
    return S

    
def DPTS(trajectory, threshold):
    """direction preserve trajectory simplication
        Given the raw trajectory and direction error threshold,
        return a simplified trajectory idx (not point) with direction error < threshold
        
        INPUT
            trajectory
            threshold: maximun direction deviation
        OUTPUT
            simplified trajectory idx list [0,1,5,8]
    """
    if len(trajectory) == 0:
        return -1
    size = len(trajectory)
    matrix = np.ones((size,size))
    matrix = np.negative(matrix)
    
    for end in range(size):
        for start in range(end):
            matrix[start,end] = Direction_error(start,end,trajectory)
    graph = {}
    for start in range(size):
    #    print start, [idx for idx,x in enumerate(matrix[start]) if x <= threshold and x >= 0]
        graph[start] = {idx:1 for idx,x in enumerate(matrix[start]) if x <= threshold and x >= 0}

    #print shortest_path(graph,0,10)
    return modified_Dijkstra(graph,0,len(trajectory)-1)

'''
    modified Dijkstra's algorithm
    O(n+m) space and O(m*log(m)) time
'''
def modified_Dijkstra(G, start, end):
   def flatten(L):       # Flatten linked list of form [0,[1,[2,[]]]]
      while len(L) > 0:
         yield L[0]
         L = L[1]

   q = [(0, start, ())]  # Heap of (cost, path_head, path_rest).
   visited = set()       # Visited vertices.
   while True:
      (cost, v1, path) = heapq.heappop(q)
      if v1 not in visited:
         visited.add(v1)
         if v1 == end:
            return list(flatten(path))[::-1] + [v1]
         path = (v1, path)
         for (v2, cost2) in G[v1].iteritems():
            if v2 not in visited:
               heapq.heappush(q, (cost + cost2, v2, path))




