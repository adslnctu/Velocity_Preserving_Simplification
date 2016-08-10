# Velocity_Preserving_Simplification

    This is a velocity preserving simplification by NCTU ADSL lab.
    It includes Adaptive Trajectory Simplification (ATS) and Non-Partition Adaptive Trajectory Simplification (NP-ATS), wihch is s streaming version of ATS

## dataset
    we use a table trajectory.taxi in pgSQL

|  Column   |            Type             | Comment                              |
|-----------|-----------------------------|--------------------------------------|
| tid       | bigint                      | unique trajectory id                 |
| index     | bigint                      | index for each point in trajectory   |
| lon       | double precision            | longitude value                      |
| lat       | double precision            | latitude value                       |
| timestamp | timestamp without time zone | point time                           |

## environment
    We use PyPy 5.1.1 as python runtime environment.
    
    #### Model
        logging: to log information
        psycopg2cffi: to connect pgSQL
        numpy
    