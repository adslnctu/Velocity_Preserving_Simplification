# Velocity_Preserving_Simplification

This is a velocity preserving simplification by NCTU ADSL lab.
It includes Adaptive Trajectory Simplification (ATS) and Non-Partition Adaptive Trajectory Simplification (NP-ATS), wihch is s streaming version of ATS

# required environment
PyPy 5.1.1 as python runtime environment.

PostgreSQL 9.5.2

* to link pgSQL correctly, you need modify dbname, user and passwd in **get_trajectory.py**, **runThresholdDecisionModel.py** and **runExperiments.py** to correct value

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



# main function

Our framework is as follows, which includes Threshold Decision Model and Adaptive Trajectory Simplification.
![framework](https://github.com/adslnctu/Velocity_Preserving_Simplification/blob/master/framework.png)

## Threshold Decision Model

**location:**  [runThresholdDecisionModel.py](https://github.com/adslnctu/Velocity_Preserving_Simplification/blob/master/runThresholdDecisionModel.py "runThresholdDecisionModel.py")


	Given a trajectory tid file and parameters, output a list of error tolerances and velocity ranges.
    1. partition trajectory by gini index to different sub-trajectory with consistent velocity
    2. use adaptive score to find the suitable epsilon of each sub-trajectory
    3. calculate the average value of epsilons in each velocity range

**args:**

| name | type | comment
|--------|--------| ----|
| -f, --file | string | input file name in **tid_list/** |
| -g, --gini | float | partition threshold (0.1, 0.9) |
| -a, --alpha | float | weight of error and compression (0.1,0.9)|
| -h, --help | | help information|

**example:**

```bash
$ pypy runThresholdDecisionModel.py -f example.txt -g 0.5 -a 0.5
Namespace(alpha=0.5, file='example.txt', gini=0.5)
INFO:root:retrieve dataset
use saved file: dataset/raw/example.txt
INFO:root:partition
INFO:root:threshold calculation
INFO:root:distribution analysis
groupID epsilon
0 17.5818491354 m
1 32.1597972196 m
2 66.5642479441 m
3 101.584648286 m
[0.0001583950372554716, 0.0002897279028794159, 0.0005996779094060433, 0.0009151770115898896]  // epsilon list

```

## Adaptive Trajectory Simplification

**location:** [simplication/ATS.py](https://github.com/adslnctu/Velocity_Preserving_Simplification/blob/master/simplification/ATS.py "simplication/ATS.py")

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

## experiments

![experiment framework](https://github.com/adslnctu/Velocity_Preserving_Simplification/blob/master/exp_framework.png)

test the comression rate, velocity error, and effectiveness for DTW, EDR, LCSS
1. read raw dataset from Database
2. simplification by different method
3. process top-k similar trajectories retrival on raw dataset
4. process top-k similar trajectories retrival on simplified dataset
5. calculate the compression rate, velocity error, and effectiveness


**location:** [runExperiments.py](https://github.com/adslnctu/Velocity_Preserving_Simplification/blob/master/runThresholdDecisionModel.py "runExperiments.py")

**args:**

| name | type | comment
|--------|--------| ----|
| -f, --file | string | input file name in **tid_list/** |
| -g, --gini | float | partition threshold (0.1 - 0.9) |
| -e, --epsilon| float | matching threshold for edr and lcss|
| -k, --topk | int | number of topk similar trajectory retrieved|
| -l, --loop | int | number of loops to get teh average values |
| --task     | string | teak name (dtw, edr, lcss) |
| -h, --help | | help informaion|

* the simplified dataset will save in **dataset/** directory
* the output file will save im **result/** directory
