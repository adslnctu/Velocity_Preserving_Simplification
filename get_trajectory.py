import psycopg2cffi
import logging

logging.basicConfig(level=logging.INFO)

def get_from_id(tid):
    conn_string = "host='127.0.0.1' dbname='NAME' user='NAME' password='PASSED'"
    conn = psycopg2cffi.connect(conn_string)
    cur = conn.cursor()
    query = "select * from trajectory.taxi where tid = " + str(tid) + " ORDER BY index;"
    logging.debug('query: '+query)
    
    try:
        cur.execute(query)
    except psycopg2cffi.Error as e:
        conn.rollback()
        cur.close()
        return logging.error('query: '+query)

    
    trajectory = []
    
    for r in cur:
        trajectory.append({'tid': int(r[0]),'index': int(r[1]),'x': r[2],'y': r[3]})

    cur.close()
    conn.close()
    return trajectory

def get_by_number(number=1):
    #conn_string = "host='192.168.100.200' dbname='vegetable' user='vegetable' password='Xup6%4M3'"
    conn_string = "host='127.0.0.1' dbname='adsl' user='adsl' password='radsl'"
    conn = psycopg2cffi.connect(conn_string)
    cur = conn.cursor()
    #query = "select tid from taxi.trajectory ORDER BY RANDOM() limit " + str(number) + ";"
    query = "select tid from trajectory.taxi group by tid limit "  + str(number) +  ";";
    
    #query = "select * from (select tid from trajectory.taxi group by tid) as T order by random()  limit 1;"
    
    logging.debug('query: '+query)
    
    try:
        cur.execute(query)
    except psycopg2cffi.Error as e:
        conn.rollback()
        cur.close()
        logging.error('query: '+query)
        return
    
    
    tid_list = [int(r[0]) for r in cur]
    

    trajectory_dataset = []
    for tid in tid_list:
        trajectory_dataset.append(get_from_id(tid))
    
    return trajectory_dataset

def get_file(file_name):

    f = open(file_name)

    tids = f.readlines()
   
    dataset = [(int(tid), get_from_id(int(tid))) for tid in tids]

    f.close()
    return dataset
    
    
def print_WKT(trajectory, S = []):
    tid = trajectory[0]['tid']
    
    if len(S) != 0:
        trajectory = [trajectory[i] for i in S]
    
    points = []
    
    for point in trajectory:
        points.append(str(point['x']) + " " + str(point['y']))
    
    print "LINESTRING (", ', '.join(points),")"
    
def WKT(trajectory, S = []):
    tid = trajectory[0]['tid']
    
    if len(S) != 0:
        trajectory = [trajectory[i] for i in S]
    
    points = []
    
    for point in trajectory:
        points.append(str(point['x']) + " " + str(point['y']))
    
    return "LINESTRING (" + ', '.join(points) + ")"
    
    
if __name__ == '__main__':
    tid = 1382270570620000011
    
    #print get_from_id(tid)
    print "get 2 trajectories"
    print get_by_number(1)
    
    print "tid:", tid
    tra = get_from_id(tid)
    S = [0,10,20]
    print "original"
    print_WKT(tra)
    print "Simpilfied"
    print_WKT(tra, S)
    
    
