import psycopg2cffi
import logging

logging.basicConfig(level=logging.INFO)

def get_from_id(tid):
    """retrieve the trajectory from database by given trajectory id
    
        INPUT
            tid: trajectory id
        
        OUTPUT
            a trajectory matching given tid
            e.g. [{x:1, y:2, tid: 1, index: 0}, {x:1.5, y:2.3, tid: 1, index: 1}, ...]
        
    """
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
    """retreive a list of trajectories from given number
        INPUT
            number: the number of retreived trajectories
        OUTPUT
            a list of trajectories
            e.g.
            [
                [{x:1, y:2, tid: 1, index: 0}, {x:1.5, y:2.3, tid: 1, index: 1}, ...]
                [{x:1, y:2, tid: 2, index: 0}, {x:1.5, y:2.3, tid: 2, index: 1}, ...]
                ...
            ]
    """
    conn_string = "host='127.0.0.1' dbname='adsl' user='adsl' password='radsl'"
    conn = psycopg2cffi.connect(conn_string)
    cur = conn.cursor()
    query = "select tid from trajectory.taxi group by tid limit "  + str(number) +  ";";
    
    
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
    """retrieve a list of trajectories from a tid list file
    
        INPUT
            file_name: the name of tid list file
                       format:
                            tid1
                            tid2
                            ...
        OUTPUT
            a list of trajectories
            e.g.
            [
                [{x:1, y:2, tid: 1, index: 0}, {x:1.5, y:2.3, tid: 1, index: 1}, ...]
                [{x:1, y:2, tid: 2, index: 0}, {x:1.5, y:2.3, tid: 2, index: 1}, ...]
                ...
            ]
    """
    f = open(file_name)

    tids = f.readlines()
   
    dataset = [(int(tid), get_from_id(int(tid))) for tid in tids]

    f.close()
    return dataset