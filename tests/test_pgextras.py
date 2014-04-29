#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

import psycopg2
import psycopg2.extras

from pgextras import PgExtras, sql_constants as sql


class TestPgextras(unittest.TestCase):
    def setUp(self):
        self.dbname = 'pgextras_unittest'
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
            self.assertTrue(pg.pg_stat_statement)

    def test_that_pg_stat_statement_is_not_installed(self):
        self.drop_pg_stat_statement()

        with PgExtras(dsn=self.dsn) as pg:
            self.assertRaises(Exception, pg.pg_stat_statement)

    def test_cache_hit(self):
        with PgExtras(dsn=self.dsn) as pg:
            results = pg.cache_hit()

        self.assertEqual(results[0].name, 'index hit rate')
        self.assertEqual(results[1].name, 'table hit rate')

    def test_version(self):
        with PgExtras(dsn=self.dsn) as pg:
            results = pg.version()

        self.assertTrue(results[0].version)

    def test_methods_have_four_tables(self):
        number_of_pgbench_tables = 4
        method_names = [
            'table_indexes_size', 'index_usage', 'seq_scans',
            'total_table_size', 'table_size', 'total_indexes_size'
        ]

        with PgExtras(dsn=self.dsn) as pg:
            for method_name in method_names:
                func = getattr(pg, method_name)
                results = func()

                self.assertTrue(len(results), number_of_pgbench_tables)

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

        blocking_cursor.close()
        blocking_conn.close()

        while not async_conn.isexecuting():
            async_cursor.close()
            async_conn.close()

        self.assertEqual(len(results), 1)

    def tearDown(self):
        self.cursor.close()
        self.conn.close()

if __name__ == '__main__':
    unittest.main()
