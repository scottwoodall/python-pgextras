# -*- coding: utf-8 -*-
import psycopg2
from . import sql_constants as sql

__author__ = 'Scott Woodall'
__email__ = 'scott.woodall@gmail.com'
__version__ = '0.1.0'


class PgExtras(object):
    def __init__(self, dsn=None):
        self.dsn = dsn
        self._pg_stat_statement = None
        self._cursor = None
        self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, trace):
        self.close_db_connection()

    @property
    def cursor(self):
        if self._cursor is None:
            self._conn = psycopg2.connect(self.dsn)
            self._cursor = self._conn.cursor()

        return self._cursor

    @property
    def pg_stat_statement(self):
        if self._pg_stat_statement is None:
            results = self.execute(sql.PG_STAT_STATEMENT)
            is_available = results[0][0]

            if is_available:
                self._pg_stat_statement = True
            else:
                raise EnvironmentError(sql.PG_STATS_NOT_AVAILABLE)

        return self._pg_stat_statement

    def close_db_connection(self):
        if self._cursor is not None:
            self._cursor.close()

        if self._conn is not None:
            self._conn.close()

    def execute(self, statement):
        # make the sql statement easier to read in case some of the queries we
        # run end up in the output
        sql = statement.replace('\n', '')
        sql = ' '.join(sql.split())
        self.cursor.execute(sql)

        return self.cursor.fetchall()

    def cache_hit(self):
        # calculates your cache hit rate (effective databases are at 99% and
        # up)

        return self.execute(sql.CACHE_HIT)

    def index_usage(self):
        # calculates your index hit rate (effective databases are at 99% and
        # up)

        return self.execute(sql.INDEX_USAGE)

    def calls(self, truncate=False):
        # show 10 most frequently called queries

        if self.pg_stat_statement:
            if truncate:
                query = """
                    SELECT CASE
                        WHEN length(query) < 40
                        THEN query
                        ELSE substr(query, 0, 38) || '..'
                    END AS qry,
                """
            else:
                query = 'SELECT query,'

            return self.execute(sql.CALLS.format(query=query))

    def blocking(self):
        # display queries holding locks other queries are waiting to be
        # released

        return self.execute(sql.BLOCKING)

    def outliers(self, truncate=False):
        # show 10 queries that have longest execution time in aggregate

        if self.pg_stat_statement:
            if truncate:
                query = """
                    CASE WHEN length(query) < 40
                        THEN query
                        ELSE substr(query, 0, 38) || '..'
                    END
                """
            else:
                query = 'query'

            return self.execute(sql.OUTLIERS.format(query=query))

    def vacuum_stats(self):
        # show dead rows and whether an automatic vacuum is expected to be
        # triggered

        return self.execute(sql.VACUUM_STATS)

    def bloat(self):
        # how table and index bloat in your database ordered by most wasteful

        return self.execute(sql.BLOAT)

    def long_running_queries(self):
        # show all queries longer than five minutes by descending duration

        return self.execute(sql.LONG_RUNNING_QUERIES)

    def seq_scans(self):
        # show the count of sequential scans by table descending by order

        return self.execute(sql.SEQ_SCANS)

    def unused_indexes(self):
        # show unused and almost unused indexes, ordered by their size relative
        # to the number of index scans. Exclude indexes of very small tables
        # (less than 5 pages), where the planner will almost invariably select
        # a sequential scan, but may not in the future as the table grows.

        return self.execute(sql.UNUSED_INDEXES)

    def total_table_size(self):
        # show the size of the tables (including indexes), descending by size

        return self.execute(sql.TOTAL_TABLE_SIZE)

    def total_indexes_size(self):
        # show the total size of all the indexes on each table, descending by
        # size

        return self.execute(sql.TOTAL_INDEXES_SIZE)

    def table_size(self):
        # show the size of the tables (excluding indexes), descending by size

        return self.execute(sql.TABLE_SIZE)

    def index_size(self):
        # show the size of indexes, descending by size

        return self.execute(sql.INDEX_SIZE)

    def total_index_size(self):
        # show the total size of all indexes in MB

        return self.execute(sql.TOTAL_INDEX_SIZE)

    def mandelbrot(self):
        # show the mandelbrot set

        return self.execute(sql.MANDELBROT)

    def locks(self):
        # display queries with active locks

        return self.execute(sql.LOCKS)

    def table_indexes_size(self):
        # show the total size of all the indexes on each table, descending by
        # size

        return self.execute(sql.TABLE_INDEXES_SIZE)
