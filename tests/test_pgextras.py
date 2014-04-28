#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pgextras
----------------------------------

Tests for `pgextras` module.
"""

import unittest

import psycopg2
import psycopg2.extras

from pgextras import PgExtras, sql_constants as sql


class TestPgextras(unittest.TestCase):
    def setUp(self):
        self.dsn = 'dbname=bench'
        self.conn = psycopg2.connect(
            self.dsn,
            cursor_factory=psycopg2.extras.NamedTupleCursor
        )
        self.cursor = self.conn.cursor()

    def drop_pg_stat_statement(self):
        statement = "DROP EXTENSION pg_stat_statements"
        self.cursor.execute(statement)
        self.conn.commit()

    def create_pg_stat_statement(self):
        statement = "CREATE EXTENSION pg_stat_statements"
        self.cursor.execute(statement)
        self.conn.commit()

    def is_pg_stat_statement_installed(self):
        self.cursor.execute(sql.PG_STAT_STATEMENT)
        results = self.cursor.fetchall()

        return results[0].available

    def test_that_pg_stat_statement_is_installed(self):
        if not self.is_pg_stat_statement_installed():
            self.create_pg_stat_statement()

        with PgExtras(dsn=self.dsn) as pg:
            self.assertTrue(pg.pg_stat_statement)

    def test_that_pg_stat_statement_is_not_installed(self):
        if self.is_pg_stat_statement_installed():
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

    def tearDown(self):
        self.cursor.close()
        self.conn.close()

if __name__ == '__main__':
    unittest.main()
