from numpy import array, zeros, argmin, inf


def eud(x,y):
    return pow( pow(x['x'] - y['x'], 2) + pow(x['y'] - y['y'], 2),0.5)
def match(x, y, ep):
    return eud(x,y) <= ep
def dtw(x, y):
    """
    Computes Dynamic Time Warping (DTW) of two sequences.

    :param array x: N1*M array
    :param array y: N2*M array
    :param func dist: distance used as cost measure

    Returns the minimum distance, the cost matrix, the accumulated cost matrix, and the wrap path.
    """
    assert len(x)
    assert len(y)
    r, c = len(x), len(y)
    D0 = zeros((r + 1, c + 1))
    D0[0, 1:] = inf
    D0[1:, 0] = inf
    D1 = D0[1:, 1:] # view
    for i in range(r):
        for j in range(c):
            D1[i, j] = eud(x[i], y[j])
    C = D1.copy()
    for i in range(r):
        for j in range(c):
            D1[i, j] += min(D0[i, j], D0[i, j+1], D0[i+1, j])
    '''
    if len(x)==1:
        path = zeros(len(y)), range(len(y))
    elif len(y) == 1:
        path = range(len(x)), zeros(len(x))
    else:
        path = _traceback(D0)
    '''
    # return D1[-1, -1] / sum(D1.shape)
    return D1[-1, -1]



def edr(sm, sn, ep):
  m,n = len(sm),len(sn)
  D = map(lambda y: map(lambda x,y : y if x==0 else x if y==0 else 0,
    range(n+1),[y]*(n+1)), range(m+1))
  for i in range(1,m+1):
    for j in range(1,n+1):
      D[i][j] = min( D[i-1][j]+1, D[i][j-1]+1, 
        D[i-1][j-1] + apply(lambda: 0 if match(sm[i-1], sn[j-1], ep) else 2)) 
  # for i in range(0,m+1):
    # print D[i] 
  # return D[m][n]
  # return D[m][n] / float(max(m,n))
  return D[m][n] / float(m+n)

  
def lcss(S, R, ep):
    len_1=len(S)

    len_2=len(R)

    x =[[0]*(len_2+1) for _ in range(len_1+1)]#the matrix whose last element ->edit distance

    for i in range(0,len_1+1): #initialization of base case values
        x[i][0]=0
        
    for j in range(0,len_2+1):
        x[0][j]=0
        
    for i in range (1,len_1+1):

        for j in range(1,len_2+1):

            if match( S[i-1], R[j-1], ep):
                x[i][j] = x[i-1][j-1] + 1

            else :
                x[i][j]= max(x[i][j-1],x[i-1][j])

    return x[i][j] / float(max(len_1, len_2))
    # return x[i][j]
    
def _traceback(D):
    i, j = array(D.shape) - 2
    p, q = [i], [j]
    while ((i > 0) or (j > 0)):
        tb = argmin((D[i, j], D[i, j+1], D[i+1, j]))
        if (tb == 0):
            i -= 1
            j -= 1
        elif (tb == 1):
            i -= 1
        else: # (tb == 2):
            j -= 1
        p.insert(0, i)
        q.insert(0, j)
    return array(p), array(q)

if __name__ == '__main__':

    x = [{'x': 0, 'y': 0}, {'x':0, 'y':1}, {'x': 1,'y': 1}, {'x': 1,'y': 2}, {'x': 2,'y': 2}, {'x': 4,'y': 3}, {'x': 2,'y': 3}, {'x': 1,'y': 1}, {'x': 2,'y': 2}, {'x': 0,'y': 1}]
    y = [{'x': 1,'y': 0}, {'x': 1,'y': 1}, {'x': 1,'y': 1}, {'x': 2,'y': 1}, {'x': 4,'y': 3}, {'x': 4,'y': 3}, {'x': 2,'y': 3}, {'x': 3,'y': 1}, {'x': 1,'y': 2}, {'x': 1,'y': 0}]
    

    dist_fun = eud
    
    dist, cost, acc, path = dtw(x, y)
    print "DTW dist:", dist
    print "LCSS dist:", lcss(x,y,0.5)
    print "EDR dist:", edr(x,y,0.5)
