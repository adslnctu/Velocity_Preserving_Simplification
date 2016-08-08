import math
import numpy as np
import heapq
from error import Position_error

"""
Find shortest path from start to end in G
"""
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

def IriImai(trajectory, threshold):
    """
        return simplified traejctory by Iri-Imai method
        
        INPUT
            trajectory
            threshold: maximun position deviation tolerance
        OUTPUT
            simplified trajectory index list with given deviation
    """
    if len(trajectory) == 0:
        return -1
    size = len(trajectory)
    matrix = np.ones((size,size))
    matrix = np.negative(matrix)
    
    for end in range(size):
        for start in range(end):
            matrix[start,end] = Position_error(start,end,trajectory)
    #print matrix
    graph = {}
    for start in range(size):
    #    print start, [idx for idx,x in enumerate(matrix[start]) if x <= threshold and x >= 0]
        graph[start] = {idx:1 for idx,x in enumerate(matrix[start]) if x <= threshold and x >= 0}

    #print shortest_path(graph,0,10)
    return modified_Dijkstra(graph,0,len(trajectory)-1)
