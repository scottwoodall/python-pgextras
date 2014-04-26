=====
Usage
=====

Your "dsn" value will be specific to the postgres database you want to connect to.
See the `postgres documentation
<http://www.postgresql.org/docs/current/static/libpq-connect.html#LIBPQ-CONNSTRING>`_
for more information on configuring connection strings::

    from pgextras import PgExtras

    with PgExtras(dsn='dbname=testing') as pg:
        results = pg.table_indexes_size()

        for row in results:
            print(row)

PgExtras Class Methods
######################

.bloat()
********
.. literalinclude:: ../pgextras/__init__.py
    :pyObject: PgExtras.bloat

.blocking()
***********
.. literalinclude:: ../pgextras/__init__.py
    :pyObject: PgExtras.blocking

.cache_hit()
************
.. literalinclude:: ../pgextras/__init__.py
    :pyObject: PgExtras.cache_hit

.calls(truncate=False)
**********************
.. literalinclude:: ../pgextras/__init__.py
    :pyObject: PgExtras.calls

.index_usage()
**************
.. literalinclude:: ../pgextras/__init__.py
    :pyObject: PgExtras.index_usage

.locks()
********
.. literalinclude:: ../pgextras/__init__.py
    :pyObject: PgExtras.locks

.long_running_queries()
***********************
.. literalinclude:: ../pgextras/__init__.py
    :pyObject: PgExtras.long_running_queries

.outliers()
***********
.. literalinclude:: ../pgextras/__init__.py
    :pyObject: PgExtras.outliers

.ps()
*****
.. literalinclude:: ../pgextras/__init__.py
    :pyObject: PgExtras.ps

.seq_scans()
*****************
.. literalinclude:: ../pgextras/__init__.py
    :pyObject: PgExtras.seq_scans

.total_table_size()
*******************
.. literalinclude:: ../pgextras/__init__.py
    :pyObject: PgExtras.total_table_size

.unused_indexes()
*****************
.. literalinclude:: ../pgextras/__init__.py
    :pyObject: PgExtras.unused_indexes

.vacuum_stats()
***************
.. literalinclude:: ../pgextras/__init__.py
    :pyObject: PgExtras.vacuum_stats

.version()
**********
.. literalinclude:: ../pgextras/__init__.py
    :pyObject: PgExtras.version
