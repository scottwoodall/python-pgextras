===============
python-pgextras
===============

.. image:: https://badge.fury.io/py/pgextras.png
    :target: http://badge.fury.io/py/pgextras

.. image:: https://travis-ci.org/scottwoodall/python-pgextras.png?branch=master
        :target: https://travis-ci.org/scottwoodall/python-pgextras

.. image:: https://pypip.in/d/pgextras/badge.png
        :target: https://pypi.python.org/pypi/pgextras

.. image:: https://coveralls.io/repos/scottwoodall/python-pgextras/badge.png
        :target: https://coveralls.io/r/scottwoodall/python-pgextras


Unofficial Python port of `Heroku's pgextras <https://github.com/heroku/heroku-pg-extras>`_
that provides various statistics for a Postgres instance. The biggest difference
of this module is that your Postgres database can be anywhere, not just
hosted with Heroku.

* BSD license
* Tested against 2.7 and 3.3
* `Documentation <http://python-pgextras.rtfd.org>`_
* `Github <https://github.com/scottwoodall/python-pgextras>`_

Features
########

Note: pgextras does not format the output as seen in all the examples below. Instead it
returns an iterable that contains namedtuples. For example, the "Total Indexes Size"
method returns the following::

    [
        Record(table='pgbench_accounts', index_size='2208 kB'),
        Record(table='pgbench_tellers', index_size='16 kB'),
        Record(table='pgbench_branches', index_size='16 kB'),
        Record(table='pgbench_history', index_size='0 bytes')
    ]

It's up to you on how to format and present the data. The results below are
formatted to make it easier to understand the data available to you.

Dev Install
###########

This is specific to the ::
    update-sql-statements branch
Clone the repository and change the branch to `update-sql-statements`
cd in to the directory and run ::
    python setup.py install
This should install the pgextras exectutable

Now, you can use any postgres database to run pgextras


Cache Hit
*********
Calculates your cache hit rate (effective databases are at 99% and up)::

    | name           |    ratio |
    |----------------+----------|
    | index hit rate | 0.999888 |
    | table hit rate | 0.999696 |

Index Usage
***********
Calculates your index hit rate (effective databases are at 99% and up)::

    | relname          |   percent_of_times_index_used |   rows_in_table |
    |------------------+-------------------------------+-----------------|
    | pgbench_history  |                               |          149985 |
    | pgbench_accounts |                            99 |          100000 |
    | pgbench_tellers  |                            96 |              10 |
    | pgbench_branches |                            93 |               1 |

Calls
*****
Show 10 most frequently called queries::

    | qry                                     | exec_time      | prop_exec_time | ncalls   | sync_io_time   |
    |-----------------------------------------+----------------+----------------+----------+----------------|
    | BEGIN;                                  | 0:00:00.140968 | 0.0%           | 414000   | 0:00:00        |
    | INSERT INTO pgbench_history (tid, bid.. | 0:00:03.788899 | 0.0%           | 414000   | 0:00:00        |
    | SELECT abalance FROM pgbench_accounts.. | 0:00:04.471754 | 0.0%           | 414000   | 0:00:00        |
    | UPDATE pgbench_accounts SET abalance .. | 0:00:21.798029 | 0.2%           | 414000   | 0:00:00        |
    | END;                                    | 0:00:00.126220 | 0.0%           | 414000   | 0:00:00        |
    | UPDATE pgbench_branches SET bbalance .. | 0:30:00.544749 | 15.9%          | 414000   | 0:00:00        |
    | UPDATE pgbench_tellers SET tbalance =.. | 2:38:45.396566 | 83.9%          | 414000   | 0:00:00        |
    | BEGIN                                   | 0:00:00.002141 | 0.0%           | 212      | 0:00:00        |
    | SELECT pid, application_name AS sourc.. | 0:00:00.039576 | 0.0%           | 77       | 0:00:00        |
    | SELECT exists( SELECT ? FROM pg_exten.. | 0:00:00.001085 | 0.0%           | 43       | 0:00:00        |


Blocking
********
Display queries holding locks other queries are waiting to be released::

    |   blocked_pid | blocking_statement                                                    | blocking_duration       |   blocking_pid | blocked_statement                                                    | blocked_duration |
    |---------------+-----------------------------------------------------------------------+-------------------------+----------------+----------------------------------------------------------------------|------------------|
    |          1688 | UPDATE pgbench_tellers SET tbalance = tbalance + -2309 WHERE tid = 9; | 0:00:00.018450          |           1724 | UPDATE pgbench_tellers SET tbalance = tbalance + -816 WHERE tid = 9; | 0:00:00.034656   |

Outliers
********
Show 10 queries that have longest execution time in aggregate::

    | qry                                     | exec_time      | prop_exec_time | ncalls   | sync_io_time   |
    |-----------------------------------------+----------------+----------------+----------+----------------|
    | UPDATE pgbench_tellers SET tbalance =.. | 2:59:30.137916 | 83.9%          | 467897   | 0:00:00        |
    | UPDATE pgbench_branches SET bbalance .. | 0:33:53.945889 | 15.8%          | 467856   | 0:00:00        |
    | UPDATE pgbench_accounts SET abalance .. | 0:00:25.384166 | 0.2%           | 467897   | 0:00:00        |
    | SELECT abalance FROM pgbench_accounts.. | 0:00:05.086917 | 0.0%           | 467897   | 0:00:00        |
    | INSERT INTO pgbench_history (tid, bid.. | 0:00:04.356031 | 0.0%           | 467848   | 0:00:00        |
    | vacuum pgbench_branches                 | 0:00:00.336647 | 0.0%           | 17       | 0:00:00        |
    | select count(*) from pgbench_accounts ; | 0:00:00.294740 | 0.0%           | 1        | 0:00:00        |
    | BEGIN;                                  | 0:00:00.160855 | 0.0%           | 467897   | 0:00:00        |
    | END;                                    | 0:00:00.142983 | 0.0%           | 467848   | 0:00:00        |
    | SELECT relname, CASE idx_scan WHEN ? .. | 0:00:00.110683 | 0.0%           | 6        | 0:00:00        |

Vacuum Stats
************
Show dead rows and whether an automatic vacuum is expected to be triggered::

    | schema   | table            | last_vacuum      | last_autovacuum   | rowcount   | dead_rowcount   | autovacuum_threshold   |   expect_autovacuum |
    |----------+------------------+------------------+-------------------+------------+-----------------+------------------------+---------------------|
    | public   | pgbench_tellers  | 2014-04-24 20:02 | 2014-04-24 20:03  | 10         | 0               | 52                     |                     |
    | public   | pgbench_branches | 2014-04-24 20:02 | 2014-04-24 20:03  | 1          | 0               | 50                     |                     |
    | public   | pgbench_history  | 2014-04-23 20:45 |                   | 15000      | 0               | 3050                  |                     |
    | public   | pgbench_accounts | 2014-04-23 20:45 |                   | 100000     | 17581          | 20050                 |                     |

Bloat
*****
Table and index bloat in your database ordered by most wasteful::

    | type   | schemaname   | object_name                                    | bloat | waste        |
    |--------+--------------+------------------------------------------------+-------+--------------|
    | table  | public       | pgbench_accounts                               | 1.3   | 3768 kB      |
    | table  | public       | pgbench_tellers                                | 19    | 144 kB       |
    | table  | public       | pgbench_branches                               | 8     | 56 kB        |

Long Running Queries
********************
Show all queries running longer than five minutes by descending duration::

    | pid   |    duration     |                                      query                                           |
    |-------+-----------------+--------------------------------------------------------------------------------------|
    | 19578 | 02:29:11.200129 | EXPLAIN SELECT  "students".* FROM "students" WHERE "students"."id" = 1450645 LIMIT 1 |
    | 19465 | 02:26:05.542653 | EXPLAIN SELECT  "students".* FROM "students" WHERE "students"."id" = 1889881 LIMIT 1 |
    | 19632 | 02:24:46.962818 | EXPLAIN SELECT  "students".* FROM "students" WHERE "students"."id" = 1581884 LIMIT 1 |

Sequence Scans
**************
Show the count of sequential scans by table descending by order::

    | name             |   count |
    |------------------+---------|
    | pgbench_branches |   57086 |
    | pgbench_tellers  |   15595 |
    | pgbench_accounts |       2 |
    | pgbench_history  |       0 |

Unused Indexes
**************
Show unused and almost unused indexes, ordered by their size relative to the
number of index scans. Exclude indexes of very small tables (less than 5
pages), where the planner will almost invariably select a sequential scan,
but may not in the future as the table grows::

    | table               |                       index                | index_size | index_scans |
    |---------------------+--------------------------------------------+------------+-------------|
    | public.grade_levels | index_placement_attempts_on_grade_level_id | 97 MB      |           0 |
    | public.observations | observations_attrs_grade_resources         | 33 MB      |           0 |
    | public.messages     | user_resource_id_idx                       | 12 MB      |           0 |

Total Table Size
****************
Show the size of the tables (including indexes), descending by size::

    | name             | size    |
    |------------------+---------|
    | pgbench_accounts | 18 MB   |
    | pgbench_history  | 2904 kB |
    | pgbench_tellers  | 272 kB  |
    | pgbench_branches | 256 kB  |

Total Indexes Size
******************
Show the total size of all the indexes on each table, descending by size::

    | table            | index_size   |
    |------------------+--------------|
    | pgbench_accounts | 2208 kB      |
    | pgbench_tellers  | 16 kB        |
    | pgbench_branches | 16 kB        |
    | pgbench_history  | 0 bytes      |

Table Size
**********
Show the size of the tables (excluding indexes), descending by size::

    | name             | size    |
    |------------------+---------|
    | pgbench_accounts | 16 MB   |
    | pgbench_history  | 2904 kB |
    | pgbench_tellers  | 256 kB  |
    | pgbench_branches | 240 kB  |

Index Size
**********
Show the size of indexes, descending by size::

    | name                  | size    |
    |-----------------------+---------|
    | pgbench_accounts_pkey | 2208 kB |
    | pgbench_tellers_pkey  | 16 kB   |
    | pgbench_branches_pkey | 16 kB   |

Total Index Size
****************
Show the total size of all indexes::

    | size    |
    |---------|
    | 2240 kB |

Locks
*****
Display queries with active locks::

     | procpid | relname | transactionid | granted |     query_snippet     |       age
     |---------+---------+---------------+---------+-----------------------+-----------------
     | 31776   |         |               | t       | <IDLE> in transaction | 00:19:29.837898
     | 31776   |         |          1294 | t       | <IDLE> in transaction | 00:19:29.837898
     | 31912   |         |               | t       | select * from hello;  | 00:19:17.94259
     | 3443    |         |               | t       |                      +| 00:00:00
     |         |         |               |         | select               +|
     |         |         |               |         | pg_stat_activi        |

Table Indexes Size
******************
Show the total size of all the indexes on each table, descending by size::

    | table            | index_size   |
    |------------------+--------------|
    | pgbench_accounts | 2208 kB      |
    | pgbench_tellers  | 16 kB        |
    | pgbench_branches | 16 kB        |
    | pgbench_history  | 0 bytes      |

PS
**
View active queries with execution time::

    |   pid | source   | running_for             |   waiting | query                                                                    |
    |-------+----------+-------------------------+-----------+--------------------------------------------------------------------------|
    | 28023 | pgbench  | 0:00:00.107013          |         0 | UPDATE pgbench_accounts SET abalance = abalance + 423 WHERE aid = 10736; |
    | 28018 | pgbench  | 0:00:00.017257          |         0 | END;                                                                     |
    | 28015 | pgbench  | 0:00:00.001055          |         1 | UPDATE pgbench_branches SET bbalance = bbalance + -4203 WHERE bid = 1;   |

Version
*******
Get the Postgres server version::

    | version                                                                                                                           |
    |-----------------------------------------------------------------------------------------------------------------------------------|
    | PostgreSQL 9.3.3 on x86_64-apple-darwin13.0.0, compiled by Apple LLVM version 5.0 (clang-500.2.79) (based on LLVM 3.3svn), 64-bit |
