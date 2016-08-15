# Velocity_Preserving_Simplification

This is a velocity preserving simplification by NCTU ADSL lab.
It includes Adaptive Trajectory Simplification (ATS) and Non-Partition Adaptive Trajectory Simplification (NP-ATS), wihch is s streaming version of ATS

# required environment
PyPy 5.1.1 as python runtime environment.

PostgreSQL 9.5.2


## dataset
we use a table trajectory.taxi in pgSQL

|  Column   |            Type             | Comment                              |
|-----------|-----------------------------|--------------------------------------|
| tid       | bigint                      | unique trajectory id                 |
| index     | bigint                      | index for each point in trajectory   |
| lon       | double precision            | longitude value                      |
| lat       | double precision            | latitude value                       |
| timestamp | timestamp without time zone | recording time                           |

and 2 indexes:
	
    "taxi_tid_index_idx" btree (tid, index)
    "taxi_lon_lat_idx" btree (lon, lat)
    



## python model

| Model Name   | Comment                |
|--------------|------------------------|
| logging      | output log information |
| psycopg2cffi | connect pgSQL          |
| numpy        | matrix calculation     |


# function

## Adaptive Trajectory Simplification

**location:** simplication/ATS.py

**function:** ATS(trajectory, min_gini)

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

## Non-Partition Adaptive Trajectory Simplification

**location:** simplication/ATS.py

**function:** NP_ATS(trajectory, min_gini)
	
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