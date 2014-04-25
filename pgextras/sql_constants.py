# -*- coding: utf-8 -*-

"""
SQL statements are kept here as to not clutter up main file.
"""


VACUUM_STATS = """
    WITH table_opts AS (
        SELECT
            pg_class.oid,
            relname,
            nspname,
            array_to_string(reloptions, '') AS relopts
        FROM pg_class
            INNER JOIN pg_namespace ns ON relnamespace = ns.oid
    ), vacuum_settings AS (
        SELECT
            oid,
            relname,
            nspname,
            CASE
                WHEN relopts LIKE '%autovacuum_vacuum_threshold%'
                THEN regexp_replace(
                    relopts,
                    '.*autovacuum_vacuum_threshold=([0-9.]+).*',
                    E'\\\\\\1'
                )::integer
                ELSE current_setting('autovacuum_vacuum_threshold')::integer
            END AS autovacuum_vacuum_threshold,
            CASE
                WHEN relopts LIKE '%autovacuum_vacuum_scale_factor%'
                THEN regexp_replace(
                    relopts,
                    '.*autovacuum_vacuum_scale_factor=([0-9.]+).*',
                    E'\\\\\\1'
                )::real
                ELSE current_setting('autovacuum_vacuum_scale_factor')::real
            END AS autovacuum_vacuum_scale_factor
        FROM table_opts
    )
    SELECT
        vacuum_settings.nspname AS schema,
        vacuum_settings.relname AS table,
        to_char(psut.last_vacuum, 'YYYY-MM-DD HH24:MI') AS last_vacuum,
        to_char(psut.last_autovacuum, 'YYYY-MM-DD HH24:MI') AS last_autovacuum,
        to_char(pg_class.reltuples, '9G999G999G999') AS rowcount,
        to_char(psut.n_dead_tup, '9G999G999G999') AS dead_rowcount,
        to_char(
            autovacuum_vacuum_threshold + (
                autovacuum_vacuum_scale_factor::numeric * pg_class.reltuples),
                '9G999G999G999'
        ) AS autovacuum_threshold,
        CASE
            WHEN autovacuum_vacuum_threshold + (
                autovacuum_vacuum_scale_factor::numeric * pg_class.reltuples
            ) < psut.n_dead_tup
            THEN 'yes'
        END AS expect_autovacuum
    FROM pg_stat_user_tables psut
        INNER JOIN pg_class ON psut.relid = pg_class.oid
        INNER JOIN vacuum_settings ON pg_class.oid = vacuum_settings.oid
    ORDER BY 1
"""

OUTLIERS = """
    SELECT {query} AS qry,
        interval '1 millisecond' * total_time AS exec_time,
        to_char((total_time/sum(total_time) OVER()) * 100,
            'FM90D0') || '%' AS
        prop_exec_time,
        to_char(calls, 'FM999G999G990') AS ncalls,
        interval '1 millisecond' * (blk_read_time + blk_write_time)
            AS sync_io_time
    FROM pg_stat_statements
    WHERE userid = (
        SELECT usesysid
        FROM pg_user
        WHERE usename = current_user
        LIMIT 1
    )
    ORDER BY total_time DESC
    LIMIT 10
"""

BLOCKING = """
    SELECT
        bl.pid AS blocked_pid,
        ka.{query_column} AS blocking_statement,
        now() - ka.query_start AS blocking_duration,
        kl.pid AS blocking_pid,
        a.{query_column} AS blocked_statement,
        now() - a.query_start AS blocked_duration
    FROM
        pg_catalog.pg_locks bl
        JOIN pg_catalog.pg_stat_activity a ON bl.pid = a.{pid_column}
        JOIN pg_catalog.pg_locks kl
        JOIN pg_catalog.pg_stat_activity ka ON kl.pid = ka.{pid_column}
            ON bl.transactionid = kl.transactionid AND bl.pid != kl.pid
    WHERE NOT bl.granted
"""

INDEX_USAGE = """
    SELECT
        relname,
        CASE idx_scan
            WHEN 0 THEN 'Insufficient data'
            ELSE (100 * idx_scan / (seq_scan + idx_scan))::text
        END percent_of_times_index_used,
        n_live_tup rows_in_table
    FROM pg_stat_user_tables
    ORDER BY n_live_tup DESC
"""

CALLS = """
    {select} interval '1 millisecond' * total_time AS exec_time,
        to_char((total_time/sum(total_time) OVER()) * 100, 'FM90D0') || '%'
            AS prop_exec_time,
        to_char(calls, 'FM999G999G990') AS ncalls,
        interval '1 millisecond' * (blk_read_time + blk_write_time)
            AS sync_io_time
    FROM pg_stat_statements
    WHERE userid = (
        SELECT usesysid
        FROM pg_user
        WHERE usename = current_user LIMIT 1
    )
    ORDER BY calls DESC
    LIMIT 10
"""

LOCKS = """
    SELECT
        pg_stat_activity.{pid_column},
        pg_class.relname,
        pg_locks.transactionid,
        pg_locks.granted,
        substr(pg_stat_activity.{query_column},1,30) AS query_snippet,
        age(now(),pg_stat_activity.query_start) AS "age"
    FROM
        pg_stat_activity,
        pg_locks LEFT OUTER JOIN pg_class ON (pg_locks.relation = pg_class.oid)
    WHERE
        pg_stat_activity.{query_column} <> '<insufficient privilege>'
            AND pg_locks.pid = pg_stat_activity.{pid_column}
            AND pg_locks.mode = 'ExclusiveLock'
            AND pg_stat_activity.{pid_column} <> pg_backend_pid()
    ORDER BY query_start
"""

PG_STAT_STATEMENT = """
    SELECT exists(
        SELECT 1
        FROM pg_extension
        WHERE extname = 'pg_stat_statements'
    ) AS available
"""

BLOAT = """
    WITH constants AS (
        SELECT
            current_setting('block_size')::numeric AS bs,
            23 AS hdr,
            4 AS ma
    ), bloat_info AS (
        SELECT
            ma,
            bs,
            schemaname,
            tablename,
            (datawidth+(
                hdr+ma-(
                    CASE
                        WHEN hdr%ma=0
                        THEN ma
                        ELSE hdr%ma
                    END
                )
            ))::numeric AS datahdr,
            (maxfracsum*(
                nullhdr+ma-(
                    CASE
                        WHEN nullhdr%ma=0
                        THEN ma
                        ELSE nullhdr%ma
                    END
                )
            )) AS nullhdr2
        FROM (
            SELECT
                schemaname,
                tablename,
                hdr,
                ma,
                bs,
                SUM((1-null_frac)*avg_width) AS datawidth,
                MAX(null_frac) AS maxfracsum,
                hdr+(
                    SELECT 1+count(*)/8
                    FROM pg_stats s2
                    WHERE
                        null_frac<>0
                        AND s2.schemaname = s.schemaname
                        AND s2.tablename = s.tablename
                ) AS nullhdr
            FROM
                pg_stats s,
                constants
            GROUP BY 1,2,3,4,5
        ) AS foo
    ), table_bloat AS (
        SELECT
            schemaname,
            tablename,
            cc.relpages,
            bs,
            CEIL(
                (cc.reltuples*(
                    (datahdr+ma-(
                        CASE
                            WHEN datahdr%ma=0
                            THEN ma
                            ELSE datahdr%ma
                        END
                    ))+nullhdr2+4
                ))/(bs-20::float)
            ) AS otta
        FROM bloat_info
            JOIN pg_class cc ON cc.relname = bloat_info.tablename
            JOIN pg_namespace nn ON cc.relnamespace = nn.oid
                AND nn.nspname = bloat_info.schemaname
                AND nn.nspname <> 'information_schema'
    ), index_bloat AS (
        SELECT
            schemaname,
            tablename,
            bs,
            COALESCE(c2.relname,'?') AS iname,
            COALESCE(c2.reltuples,0) AS ituples,
            COALESCE(c2.relpages,0) AS ipages,
            COALESCE(
                CEIL((c2.reltuples*(datahdr-12))/(bs-20::float)),0
            ) AS iotta
        FROM bloat_info
            JOIN pg_class cc ON cc.relname = bloat_info.tablename
            JOIN pg_namespace nn ON cc.relnamespace = nn.oid
                AND nn.nspname = bloat_info.schemaname
                AND nn.nspname <> 'information_schema'
            JOIN pg_index i ON indrelid = cc.oid
            JOIN pg_class c2 ON c2.oid = i.indexrelid
     )
     SELECT
        type,
        schemaname,
        object_name,
        bloat,
        pg_size_pretty(raw_waste) AS waste
     FROM (
        SELECT
            'table' AS type,
            schemaname,
            tablename AS object_name,
            ROUND(
                CASE
                    WHEN otta=0
                    THEN 0.0
                    ELSE table_bloat.relpages/otta::numeric
                END,
            1) AS bloat,
            CASE
                WHEN relpages < otta
                THEN '0'
                ELSE (bs*(
                    table_bloat.relpages-otta)::bigint)::bigint
            END AS raw_waste
        FROM table_bloat
        UNION
        SELECT
            'index' AS type,
            schemaname,
            tablename || '::' || iname AS object_name,
            ROUND(
                CASE
                    WHEN iotta=0 OR ipages=0
                    THEN 0.0
                    ELSE ipages/iotta::numeric
                END,
            1) AS bloat,
            CASE
                WHEN ipages < iotta
                THEN '0'
                ELSE (bs*(ipages-iotta))::bigint
            END AS raw_waste
        FROM index_bloat
    ) bloat_summary
    ORDER BY
        raw_waste DESC,
        bloat DESC
"""

LONG_RUNNING_QUERIES = """
     SELECT
        {pid_column},
        now() - pg_stat_activity.query_start AS duration,
        {query_column} AS query
    FROM pg_stat_activity
    WHERE
        pg_stat_activity.{query_column} <> ''::text
        {idle}
        AND now() - pg_stat_activity.query_start > interval '5 minutes'
    ORDER BY now() - pg_stat_activity.query_start DESC
"""

SEQ_SCANS = """
     SELECT
        relname AS name,
        seq_scan AS count
     FROM pg_stat_user_tables
     ORDER BY seq_scan DESC
"""

UNUSED_INDEXES = """
    SELECT
        schemaname || '.' || relname AS table,
        indexrelname AS index,
        pg_size_pretty(pg_relation_size(i.indexrelid)) AS index_size,
        idx_scan AS index_scans
    FROM pg_stat_user_indexes ui
        JOIN pg_index i ON ui.indexrelid = i.indexrelid
    WHERE
        NOT indisunique AND idx_scan < 50
        AND pg_relation_size(relid) > 5 * 8192
    ORDER BY
        pg_relation_size(i.indexrelid) / nullif(idx_scan, 0) DESC
        NULLS FIRST,
        pg_relation_size(i.indexrelid) DESC
"""

TOTAL_TABLE_SIZE = """
    SELECT
        c.relname AS name,
        pg_size_pretty(pg_total_relation_size(c.oid)) AS size
    FROM pg_class c
        LEFT JOIN pg_namespace n ON (n.oid = c.relnamespace)
    WHERE
        n.nspname NOT IN ('pg_catalog', 'information_schema')
        AND n.nspname !~ '^pg_toast'
        AND c.relkind='r'
    ORDER BY pg_total_relation_size(c.oid) DESC
"""

TOTAL_INDEXES_SIZE = """
    SELECT
        c.relname AS table,
        pg_size_pretty(pg_indexes_size(c.oid)) AS index_size
    FROM pg_class c
        LEFT JOIN pg_namespace n ON (n.oid = c.relnamespace)
    WHERE
        n.nspname NOT IN ('pg_catalog', 'information_schema')
        AND n.nspname !~ '^pg_toast'
        AND c.relkind='r'
    ORDER BY pg_indexes_size(c.oid) DESC;
"""

TABLE_SIZE = """
     SELECT
        c.relname AS name,
        pg_size_pretty(pg_table_size(c.oid)) AS size
     FROM pg_class c
        LEFT JOIN pg_namespace n ON (n.oid = c.relnamespace)
     WHERE
        n.nspname NOT IN ('pg_catalog', 'information_schema')
        AND n.nspname !~ '^pg_toast'
        AND c.relkind='r'
     ORDER BY pg_table_size(c.oid) DESC
"""

INDEX_SIZE = """
    SELECT
        c.relname AS name,
        pg_size_pretty(sum(c.relpages::bigint*8192)::bigint) AS size
    FROM pg_class c
        LEFT JOIN pg_namespace n ON (n.oid = c.relnamespace)
    WHERE
        n.nspname NOT IN ('pg_catalog', 'information_schema')
        AND n.nspname !~ '^pg_toast'
        AND c.relkind='i'
    GROUP BY c.relname
    ORDER BY sum(c.relpages) DESC
"""

TOTAL_INDEX_SIZE = """
    SELECT pg_size_pretty(sum(c.relpages::bigint*8192)::bigint) AS size
    FROM pg_class c
        LEFT JOIN pg_namespace n ON (n.oid = c.relnamespace)
    WHERE
        n.nspname NOT IN ('pg_catalog', 'information_schema')
        AND n.nspname !~ '^pg_toast'
        AND c.relkind='i';
"""

CACHE_HIT = """
    SELECT
        'index hit rate' AS name,
        (sum(idx_blks_hit)) / sum(idx_blks_hit + idx_blks_read) AS ratio
    FROM pg_statio_user_indexes
    UNION ALL
    SELECT
        'table hit rate' AS name,
        sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read))
            AS ratio
    FROM pg_statio_user_tables
"""

TABLE_INDEXES_SIZE = """
    SELECT
        c.relname AS table,
        pg_size_pretty(pg_indexes_size(c.oid)) AS index_size
    FROM pg_class c
        LEFT JOIN pg_namespace n ON (n.oid = c.relnamespace)
    WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
        AND n.nspname !~ '^pg_toast'
        AND c.relkind='r'
    ORDER BY pg_indexes_size(c.oid) DESC;
"""

PG_STATS_NOT_AVAILABLE = """
    pg_stat_statements extension needs to be installed in the
    public schema first. This extension is only available on
    Postgres versions 9.2 or greater. You can install it by
    adding pg_stat_statements to shared_preload_libraries in
    postgresql.conf, restarting postgres and then running the
    following sql statement in your database:
    CREATE EXTENSION pg_stat_statements;
"""

PS = """
    SELECT
        {pid_column},
        application_name AS source,
        age(now(),query_start) AS running_for,
        waiting,
        {query_column} AS query
    FROM pg_stat_activity
    WHERE {query_column} <> '<insufficient privilege>'
        AND {pid_column} <> pg_backend_pid()
        {idle}
    ORDER BY query_start DESC
"""

VERSION = """
    SELECT version()
"""
