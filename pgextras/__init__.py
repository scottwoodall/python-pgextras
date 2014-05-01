# -*- coding: utf-8 -*-
import re

import psycopg2
import psycopg2.extras

from . import sql_constants as sql

__author__ = 'Scott Woodall'
__email__ = 'scott.woodall@gmail.com'
__version__ = '0.1.1'


class PgExtras(object):
    def __init__(self, dsn=None):
        self.dsn = dsn
        self._pg_stat_statement = None
        self._cursor = None
        self._conn = None
        self._is_pg_at_least_nine_two = None

    def __enter__(self):
        """
        The context manager convention is preferred so that if there are ever
        any exceptions the database cursor/connection will always be closed.
        """
        return self

    def __exit__(self, type, value, trace):
        self.close_db_connection()

    @property
    def cursor(self):
        if self._cursor is None:
            self._conn = psycopg2.connect(
                self.dsn,
                cursor_factory=psycopg2.extras.NamedTupleCursor
            )

            self._cursor = self._conn.cursor()

        return self._cursor

    @property
    def query_column(self):
        """
        PG9.2 changed column names.

        :returns: str
        """

        if self.is_pg_at_least_nine_two():
            return 'query'
        else:
            return 'current_query'

    @property
    def pid_column(self):
        """
        PG9.2 changed column names.

        :returns: str
        """

        if self.is_pg_at_least_nine_two():
            return 'pid'
        else:
            return 'procpid'

    def pg_stat_statement(self):
        """
        Some queries require the pg_stat_statement module to be installed.
        http://www.postgresql.org/docs/current/static/pgstatstatements.html

        :returns: boolean
        """

        if self._pg_stat_statement is None:
            results = self.execute(sql.PG_STAT_STATEMENT)
            is_available = results[0].available

            if is_available:
                self._pg_stat_statement = True
            else:
                raise Exception("""
                    pg_stat_statements extension needs to be installed in the
                    public schema first. This extension is only available on
                    Postgres versions 9.2 or greater. You can install it by
                    adding pg_stat_statements to shared_preload_libraries in
                    postgresql.conf, restarting postgres and then running the
                    following sql statement in your database:
                    CREATE EXTENSION pg_stat_statements;
                """)

        return self._pg_stat_statement

    def is_pg_at_least_nine_two(self):
        """
        Some queries have different syntax depending what version of postgres
        we are querying against.

        :returns: boolean
        """

        if self._is_pg_at_least_nine_two is None:
            results = self.version()
            regex = re.compile("PostgreSQL (\d+\.\d+\.\d+) on")
            matches = regex.match(results[0].version)
            version = matches.groups()[0]

            if version > '9.2.0':
                self._is_pg_at_least_nine_two = True
            else:
                self._is_pg_at_least_nine_two = False

        return self._is_pg_at_least_nine_two

    def close_db_connection(self):
        if self._cursor is not None:
            self._cursor.close()

        if self._conn is not None:
            self._conn.close()

    def execute(self, statement):
        """
        Execute the given sql statement.

        :param statement: sql statement to run
        :returns: list
        """

        # Make the sql statement easier to read in case some of the queries we
        # run end up in the output
        sql = statement.replace('\n', '')
        sql = ' '.join(sql.split())
        self.cursor.execute(sql)

        return self.cursor.fetchall()

    def cache_hit(self):
        """
        Calculates your cache hit rate (effective databases are at 99% and up).

        Record(
            name='index hit rate',
            ratio=Decimal('0.99994503346970922117')
        )

        :returns: list of Records
        """

        return self.execute(sql.CACHE_HIT)

    def index_usage(self):
        """
        Calculates your index hit rate (effective databases are at 99% and up).

        Record(
            relname='pgbench_history',
            percent_of_times_index_used=None,
            rows_in_table=249976
        )

        :returns: list of Records
        """

        return self.execute(sql.INDEX_USAGE)

    def calls(self, truncate=False):
        """
        Show 10 most frequently called queries. Requires the pg_stat_statements
        Postgres module to be installed.

        Record(
            query='BEGIN;',
            exec_time=datetime.timedelta(0, 0, 288174),
            prop_exec_time='0.0%',
            ncalls='845,590',
            sync_io_time=datetime.timedelta(0)
        )

        :param truncate: trim the Record.query output if greater than 40 chars
        :returns: list of Records
        """

        if self.pg_stat_statement():
            if truncate:
                select = """
                    SELECT CASE
                        WHEN length(query) < 40
                        THEN query
                        ELSE substr(query, 0, 38) || '..'
                    END AS qry,
                """
            else:
                select = 'SELECT query,'

            return self.execute(sql.CALLS.format(select=select))

    def blocking(self):
        """
        Display queries holding locks other queries are waiting to be
        released.

        Record(
            pid=40821,
            source='',
            running_for=datetime.timedelta(0, 0, 2857),
            waiting=False,
            query='SELECT pg_sleep(10);'
        )

        :returns: list of Records
        """

        return self.execute(
            sql.BLOCKING.format(
                query_column=self.query_column,
                pid_column=self.pid_column
            )
        )

    def outliers(self, truncate=False):
        """
        Show 10 queries that have longest execution time in aggregate. Requires
        the pg_stat_statments Postgres module to be installed.

        Record(
            qry='UPDATE pgbench_tellers SET tbalance = tbalance + ?;',
            exec_time=datetime.timedelta(0, 19944, 993099),
            prop_exec_time='67.1%',
            ncalls='845,589',
            sync_io_time=datetime.timedelta(0)
        )

        :param truncate: trim the Record.qry output if greater than 40 chars
        :returns: list of Records
        """

        if self.pg_stat_statement():
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
        """
        Show dead rows and whether an automatic vacuum is expected to be
        triggered.

        Record(
            schema='public',
            table='pgbench_tellers',
            last_vacuum='2014-04-29 14:45',
            last_autovacuum='2014-04-29 14:45',
            rowcount='10',
            dead_rowcount='0',
            autovacuum_threshold='52',
            expect_autovacuum=None
        )

        :returns: list of Records
        """

        return self.execute(sql.VACUUM_STATS)

    def bloat(self):
        """
        Table and index bloat in your database ordered by most wasteful.

        Record(
            type='index',
            schemaname='public',
            object_name='pgbench_accounts::pgbench_accounts_pkey',
            bloat=Decimal('0.2'),
            waste='0 bytes'
        )

        :returns: list of Records
        """

        return self.execute(sql.BLOAT)

    def long_running_queries(self):
        """
        Show all queries longer than five minutes by descending duration.

        Record(
            pid=19578,
            duration=datetime.timedelta(0, 19944, 993099),
            query='SELECT * FROM students'
        )

        :returns: list of Records
        """

        if self.is_pg_at_least_nine_two():
            idle = "AND state <> 'idle'"
        else:
            idle = "AND current_query <> '<IDLE>'"

        return self.execute(
            sql.LONG_RUNNING_QUERIES.format(
                pid_column=self.pid_column,
                query_column=self.query_column,
                idle=idle
            )
        )

    def seq_scans(self):
        """
        Show the count of sequential scans by table descending by order.

        Record(
            name='pgbench_branches',
            count=237
        )

        :returns: list of Records
        """

        return self.execute(sql.SEQ_SCANS)

    def unused_indexes(self):
        """
        Show unused and almost unused indexes, ordered by their size relative
        to the number of index scans. Exclude indexes of very small tables
        (less than 5 pages), where the planner will almost invariably select
        a sequential scan, but may not in the future as the table grows.

        Record(
            table='public.grade_levels',
            index='index_placement_attempts_on_grade_level_id',
            index_size='97 MB',
            index_scans=0
        )

        :returns: list of Records
        """

        return self.execute(sql.UNUSED_INDEXES)

    def total_table_size(self):
        """
        Show the size of the tables (including indexes), descending by size.

        Record(
            name='pgbench_accounts',
            size='15 MB'
        )

        :returns: list of Records
        """

        return self.execute(sql.TOTAL_TABLE_SIZE)

    def total_indexes_size(self):
        """
        Show the total size of all the indexes on each table, descending by
        size.

        Record(
            table='pgbench_accounts',
            index_size='2208 kB'
        )

        :returns: list of Records
        """

        return self.execute(sql.TOTAL_INDEXES_SIZE)

    def table_size(self):
        """
        Show the size of the tables (excluding indexes), descending by size.

        :returns: list
        """

        return self.execute(sql.TABLE_SIZE)

    def index_size(self):
        """
        Show the size of indexes, descending by size.

        :returns: list
        """

        return self.execute(sql.INDEX_SIZE)

    def total_index_size(self):
        """
        Show the total size of all indexes.

        Record(
            size='2240 kB'
        )

        :returns: list of Records
        """

        return self.execute(sql.TOTAL_INDEX_SIZE)

    def locks(self):
        """
        Display queries with active locks.

        Record(
            procpid=31776,
            relname=None,
            transactionid=None,
            granted=True,
            query_snippet='select * from hello;',
            age=datetime.timedelta(0, 0, 288174),
        )

        :returns: list of Records
        """

        return self.execute(
            sql.LOCKS.format(
                pid_column=self.pid_column,
                query_column=self.query_column
            )
        )

    def table_indexes_size(self):
        """
        Show the total size of all the indexes on each table, descending by
        size.

        Record(
            table='pgbench_accounts',
            index_size='2208 kB'
        )

        :returns: list of Records
        """

        return self.execute(sql.TABLE_INDEXES_SIZE)

    def ps(self):
        """
        View active queries with execution time.

        Record(
            pid=28023,
            source='pgbench',
            running_for=datetime.timedelta(0, 0, 288174),
            waiting=0,
            query='UPDATE pgbench_accounts SET abalance = abalance + 423;'
        )

        :returns: list of Records
        """

        if self.is_pg_at_least_nine_two():
            idle = "AND state <> 'idle'"
        else:
            idle = "AND current_query <> '<IDLE>'"

        return self.execute(
            sql.PS.format(
                pid_column=self.pid_column,
                query_column=self.query_column,
                idle=idle
            )
        )

    def version(self):
        """
        Get the Postgres server version.

        Record(
            version='PostgreSQL 9.3.3 on x86_64-apple-darwin13.0.0'
        )

        :returns: list of Records
        """

        return self.execute(sql.VERSION)
