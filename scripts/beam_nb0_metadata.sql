-- Query 1: Column catalog for all tables
-- Maps directly to Column(name, type, description) in the semantic layer.
SELECT
    c.table_schema,
    c.table_name,
    c.ordinal_position                                       AS pos,
    c.column_name,
    c.data_type,
    c.is_nullable,
    pgd.description                                          AS pg_comment,
    CASE WHEN pk.column_name IS NOT NULL THEN true
         ELSE false END                                      AS is_primary_key
FROM information_schema.columns c
LEFT JOIN pg_class pgc
       ON pgc.relname = c.table_name
      AND pgc.relnamespace = (
              SELECT oid FROM pg_namespace WHERE nspname = c.table_schema)
LEFT JOIN pg_description pgd
       ON pgd.objoid = pgc.oid
      AND pgd.objsubid = c.ordinal_position
LEFT JOIN (
    SELECT ku.table_schema, ku.table_name, ku.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage ku
      ON tc.constraint_name = ku.constraint_name
     AND tc.table_schema    = ku.table_schema
    WHERE tc.constraint_type = 'PRIMARY KEY'
) pk ON pk.table_schema = c.table_schema
    AND pk.table_name   = c.table_name
    AND pk.column_name  = c.column_name
WHERE c.table_schema NOT IN ('pg_catalog', 'information_schema', 'marts')
ORDER BY c.table_schema, c.table_name, c.ordinal_position;


-- Query 2: Sample rows (3 rows per table)
SELECT * FROM public.users           LIMIT 3;
SELECT * FROM public.payments        LIMIT 3;
SELECT * FROM public.sessions        LIMIT 3;
SELECT * FROM public.subscriptions   LIMIT 3;


-- Query 3: Column statistics for all tables
-- Spot high-null or near-unique columns to consider excluding from the semantic layer.
SELECT
    schemaname,
    tablename,
    attname        AS column_name,
    null_frac,
    n_distinct,
    most_common_vals::text
FROM pg_stats
WHERE schemaname NOT IN ('pg_catalog', 'information_schema', 'marts')
ORDER BY schemaname, tablename, attname;
