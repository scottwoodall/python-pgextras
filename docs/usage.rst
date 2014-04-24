========
Usage
========

To use python-pgextras in a project::

    from pgextras import PgExtras

    with PgExtras(dsn='dbname=testing') as pg:
        results = pg.table_indexes_size()

        if results is not None:
            for row in results:
                print(row)
