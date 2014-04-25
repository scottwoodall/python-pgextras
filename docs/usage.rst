========
Usage
========

Your "dsn" value will be specific to the postgres database you want to connect to.
See the `postgres documentation
<http://www.postgresql.org/docs/current/static/libpq-connect.html#LIBPQ-CONNSTRING>`_
for more information on configuring connection strings::

    from pgextras import PgExtras

    with PgExtras(dsn='dbname=testing') as pg:
        results = pg.table_indexes_size()

        if results is not None:
            for row in results:
                print(row)

PgExtras Class Methods
######################

.cache_hit()
************
Calculates your cache hit rate (effective databases are at 99% and up).

.index_usage()
**************
Calculates your index hit rate (effective databases are at 99% and up).

.calls()
********
Show 10 most frequently called queries.

.blocking()
***********
Display queries holding locks other queries are waiting to be released.

.outliers()
***********
Show 10 queries that have longest execution time in aggregate.

.vacuum_stats()
***************
Show dead rows and whether an automatic vacuum is expected to be triggered.

.bloat()
********
Table and index bloat in your database ordered by most wasteful.

.long_running_queries()
***********************
Show all queries running longer than five minutes by descending duration.

.sequence_scans()
*****************
Show the count of sequential scans by table descending by order.

.unused_indexes()
*****************
Show unused and almost unused indexes, ordered by their size relative to the
number of index scans. Exclude indexes of very small tables (less than 5
pages), where the planner will almost invariably select a sequential scan,
but may not in the future as the table grows.

.total_table_size()
*******************
Show the size of the tables (including indexes), descending by size.

.locks()
********
Display queries with active locks.

.ps()
*****
View active queries with execution time.

.version()
**********
Get the Postgres server version.
