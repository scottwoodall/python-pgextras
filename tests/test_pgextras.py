#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from mock import patch
import psycopg2
import psycopg2.extras

from pgextras import PgExtras, sql_constants as sql


class TestPgextras(unittest.TestCase):
    def setUp(self):
        self.dbname = 'python_pgextras_unittest'
        self.dsn = 'dbname={dbname}'.format(dbname=self.dbname)
        self.conn = psycopg2.connect(
            self.dsn,
            cursor_factory=psycopg2.extras.NamedTupleCursor
        )
        self.cursor = self.conn.cursor()

    def drop_pg_stat_statement(self):
        if self.is_pg_stat_statement_installed():
            statement = "DROP EXTENSION pg_stat_statements"
            self.cursor.execute(statement)
            self.conn.commit()

    def create_pg_stat_statement(self):
        if not self.is_pg_stat_statement_installed():
            statement = "CREATE EXTENSION pg_stat_statements"
            self.cursor.execute(statement)
            self.conn.commit()

    def is_pg_stat_statement_installed(self):
        self.cursor.execute(sql.PG_STAT_STATEMENT)
        results = self.cursor.fetchall()

        return results[0].available

    def test_that_pg_stat_statement_is_installed(self):
        self.create_pg_stat_statement()

        with PgExtras(dsn=self.dsn) as pg:
            self.assertTrue(pg.pg_stat_statement())

    def test_that_pg_stat_statement_is_not_installed(self):
        self.drop_pg_stat_statement()

        with PgExtras(dsn=self.dsn) as pg:
            self.assertRaises(Exception, pg.pg_stat_statement)

    def test_methods_have_one_result(self):
        method_names = ['version', 'total_index_size']

        with PgExtras(dsn=self.dsn) as pg:
            for method_name in method_names:
                func = getattr(pg, method_name)
                results = func()

                self.assertTrue(len(results), 1)

    def test_methods_have_two_results(self):
        method_names = ['cache_hit']

        with PgExtras(dsn=self.dsn) as pg:
            for method_name in method_names:
                func = getattr(pg, method_name)
                results = func()

                self.assertTrue(len(results), 2)

    def test_methods_have_three_results(self):
        method_names = ['index_size']

        with PgExtras(dsn=self.dsn) as pg:
            for method_name in method_names:
                func = getattr(pg, method_name)
                results = func()

                self.assertEqual(len(results), 3)

    def test_methods_have_four_results(self):
        method_names = [
            'table_indexes_size', 'index_usage', 'seq_scans',
            'total_table_size', 'table_size', 'total_indexes_size'
        ]

        with PgExtras(dsn=self.dsn) as pg:
            for method_name in method_names:
                func = getattr(pg, method_name)
                results = func()

                self.assertTrue(len(results), 4)

    def test_calls(self):
        with PgExtras(dsn=self.dsn) as pg:
            if pg.is_pg_at_least_nine_two():
                self.create_pg_stat_statement()
                results = pg.calls()
                self.assertTrue(len(results), 10)
            else:
                self.assertRaises(Exception, pg.calls)

    def test_blocking(self):
        statement = """
            UPDATE pgbench_branches
            SET bbalance = bbalance + 10
            WHERE bid = 1
        """

        blocking_conn = psycopg2.connect(
            database=self.dbname,
            cursor_factory=psycopg2.extras.NamedTupleCursor
        )

        blocking_cursor = blocking_conn.cursor()
        blocking_cursor.execute(statement)

        async_conn = psycopg2.connect(
            database=self.dbname,
            cursor_factory=psycopg2.extras.NamedTupleCursor,
            async=1
        )

        psycopg2.extras.wait_select(async_conn)
        async_cursor = async_conn.cursor()
        async_cursor.execute(statement)

        with PgExtras(dsn=self.dsn) as pg:
            results = pg.blocking()

        self.assertEqual(len(results), 1)

    def test_ps(self):
        """
        If the test suite is ran back to back within one second of each other
        there is a race condition and this test has the potential to fail.
        There will be more than one result because the previous test suites run
        of pg_sleep(2) is still in the pg_stat_activity table. There's also a
        race condition that pg.ps() does not return within 2 seconds and the
        sleep is already gone from the pg_stat_activity.
        """

        statement = """
            SELECT pg_sleep(2);
        """

        async_conn = psycopg2.connect(
            database=self.dbname,
            cursor_factory=psycopg2.extras.NamedTupleCursor,
            async=1
        )

        psycopg2.extras.wait_select(async_conn)
        async_cursor = async_conn.cursor()
        async_cursor.execute(statement)

        with PgExtras(dsn=self.dsn) as pg:
            results = pg.ps()

        self.assertEqual(len(results), 1)

    @patch.object(PgExtras, 'is_pg_at_least_nine_two')
    def test_that_pid_column_returns_correct_column_name(self, mockery):
        mockery.return_value = False

        with PgExtras(dsn=self.dsn) as pg:
            self.assertEqual(pg.pid_column,  'procpid')
            mockery.return_value = True
            self.assertEqual(pg.pid_column,  'pid')

    @patch.object(PgExtras, 'is_pg_at_least_nine_two')
    def test_that_query_column_returns_correct_column_name(self, mockery):
        mockery.return_value = False

        with PgExtras(dsn=self.dsn) as pg:
            self.assertEqual(pg.query_column,  'current_query')
            mockery.return_value = True
            self.assertEqual(pg.query_column,  'query')

    @patch.object(PgExtras, 'version')
    def test_parsing_postgres_version_number(self, mockery):
        Record = type('Record', (object, ), {
            'version': 'PostgreSQL 9.3.3 on x86_64-apple-darwin13.0.0'
        })
        mockery.return_value = [Record]

        with PgExtras(dsn=self.dsn) as pg:
            self.assertTrue(pg.is_pg_at_least_nine_two())
            Record.version = 'PostgreSQL 9.1.1 on x86_64-apple-darwin13.0.0'
            pg._is_pg_at_least_nine_two = None
            self.assertFalse(pg.is_pg_at_least_nine_two())

    def tearDown(self):
        self.cursor.close()
        self.conn.close()

if __name__ == '__main__':
    unittest.main()
