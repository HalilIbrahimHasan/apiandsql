# ============================================================
# PostgreSQL Hands-on SQL (Python + SQLAlchemy)
# Single file: DDL + DML + Queries + Recreate flow
# ============================================================

from sqlalchemy import create_engine, text  # SQLAlchemy engine + raw SQL execution
from sqlalchemy.engine import Engine        # Type hint
from datetime import datetime               # For timestamps in printouts


# ✅ Database connection string (update user/pass/db if needed)
DB_URL = "postgresql+psycopg2://selma:1234@localhost:5432/postgres"

# ✅ Create engine (future=True gives modern SQLAlchemy behavior)
engine: Engine = create_engine(DB_URL, future=True)


# ------------------------------------------------------------
# Helper: print section headers
# ------------------------------------------------------------
def banner(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


# ------------------------------------------------------------
# Helper: run a SQL statement (no returned rows)
# ------------------------------------------------------------
def exec_sql(conn, sql: str, params: dict | None = None) -> None:
    conn.execute(text(sql), params or {})  # Execute raw SQL safely with parameters


# ------------------------------------------------------------
# Helper: run a SELECT and print results
# ------------------------------------------------------------
def query_and_print(conn, sql: str, params: dict | None = None, limit: int | None = 50) -> None:
    result = conn.execute(text(sql), params or {})  # Run query
    rows = result.fetchall()                        # Fetch all rows
    cols = result.keys()                            # Column names

    print(f"\nSQL:\n{sql.strip()}\n")
    print(f"Rows returned: {len(rows)}")

    # Print header
    print(" | ".join(cols))
    print("-" * 70)

    # Print rows (optionally limit)
    to_show = rows if limit is None else rows[:limit]
    for r in to_show:
        print(" | ".join(str(x) for x in r))

    if limit is not None and len(rows) > limit:
        print(f"... ({len(rows) - limit} more rows)")


# ------------------------------------------------------------
# 1) Clean start: Drop tables if they exist (safe reset)
# ------------------------------------------------------------
def reset_schema(conn) -> None:
    banner("0) CLEAN START (DROP TABLES IF EXISTS)")
    exec_sql(conn, "DROP TABLE IF EXISTS archived_results;")
    exec_sql(conn, "DROP TABLE IF EXISTS results;")
    exec_sql(conn, "DROP TABLE IF EXISTS orders;")
    print("Dropped tables if they existed ✅")


# ------------------------------------------------------------
# 2) Create tables (DDL)
# ------------------------------------------------------------
def create_tables(conn) -> None:
    banner("1) CREATE TABLES (DDL)")

    exec_sql(conn, """
    CREATE TABLE orders (
      order_id      INT PRIMARY KEY,
      patient_id    INT NOT NULL,
      ordered_at    TIMESTAMP NOT NULL DEFAULT now(),
      status        TEXT NOT NULL
    );
    """)

    exec_sql(conn, """
    CREATE TABLE results (
      result_id     INT PRIMARY KEY,
      order_id      INT NOT NULL REFERENCES orders(order_id),
      test_name     TEXT NOT NULL,
      value         NUMERIC(10,2),
      unit          TEXT,
      flag          TEXT,
      performed_at  TIMESTAMP NOT NULL DEFAULT now(),
      doctor_reviewed_by TEXT NULL
    );
    """)

    exec_sql(conn, """
    CREATE TABLE archived_results (
      result_id     INT PRIMARY KEY,
      order_id      INT NOT NULL,
      test_name     TEXT NOT NULL,
      value         NUMERIC(10,2),
      unit          TEXT,
      flag          TEXT,
      performed_at  TIMESTAMP NOT NULL,
      doctor_reviewed_by TEXT NULL
    );
    """)

    print("Tables created ✅")


# ------------------------------------------------------------
# 3) Insert data (DML)
# ------------------------------------------------------------
def seed_data(conn) -> None:
    banner("2) INSERT SAMPLE DATA (DML)")

    exec_sql(conn, """
    INSERT INTO orders (order_id, patient_id, ordered_at, status) VALUES
    (1001, 1009, '2026-02-07 00:10:00', 'published'),
    (1002, 1010, '2026-02-07 00:12:00', 'draft'),
    (1003, 1009, '2026-02-07 00:24:43', 'published');
    """)

    exec_sql(conn, """
    INSERT INTO results (result_id, order_id, test_name, value, unit, flag, performed_at, doctor_reviewed_by) VALUES
    (8001, 1001, 'Glucose (fasting)', 92.00, 'mg/dL', 'normal', '2026-02-07 00:10:30', NULL),
    (8002, 1003, 'BUN',              18.90, 'mg/dL', 'normal', '2026-02-07 00:24:43', NULL),
    (8003, 1003, 'Creatinine',        0.72, 'mg/dL', 'normal', '2026-02-07 00:24:43', NULL),
    (8004, 1002, 'HbA1c',             6.10, '%',     'high',   '2026-02-07 00:12:20', 'Dr. Lee');
    """)

    exec_sql(conn, """
    INSERT INTO archived_results (result_id, order_id, test_name, value, unit, flag, performed_at, doctor_reviewed_by) VALUES
    (7001,  999, 'BUN',        19.20, 'mg/dL', 'normal', '2026-01-01 09:00:00', NULL),
    (7002,  999, 'Creatinine',  0.80, 'mg/dL', 'normal', '2026-01-01 09:00:00', 'Dr. Kim');
    """)

    print("Sample data inserted ✅")

    # Quick verification queries
    query_and_print(conn, "SELECT * FROM orders ORDER BY order_id;")
    query_and_print(conn, "SELECT * FROM results ORDER BY result_id;")
    query_and_print(conn, "SELECT * FROM archived_results ORDER BY result_id;")


# ------------------------------------------------------------
# 4) DELETE vs TRUNCATE vs DROP (and recreate after DROP)
# ------------------------------------------------------------
def delete_truncate_drop_demo(conn) -> None:
    banner("3) DELETE vs TRUNCATE vs DROP")

    # --- DELETE: remove one row using WHERE
    banner("3A) DELETE (single row)")
    query_and_print(conn, "SELECT result_id, test_name FROM results ORDER BY result_id;")
    exec_sql(conn, "DELETE FROM results WHERE result_id = 8001;")
    print("Deleted result_id=8001 ✅")
    query_and_print(conn, "SELECT result_id, test_name FROM results ORDER BY result_id;")

    # Re-insert deleted row so future demos remain consistent
    exec_sql(conn, """
    INSERT INTO results (result_id, order_id, test_name, value, unit, flag, performed_at, doctor_reviewed_by)
    VALUES (8001, 1001, 'Glucose (fasting)', 92.00, 'mg/dL', 'normal', '2026-02-07 00:10:30', NULL);
    """)
    print("Re-inserted result_id=8001 ✅")

    # --- TRUNCATE: empty entire archived_results table fast
    banner("3B) TRUNCATE (empty table)")
    query_and_print(conn, "SELECT * FROM archived_results ORDER BY result_id;")
    exec_sql(conn, "TRUNCATE TABLE archived_results;")
    print("Truncated archived_results ✅")
    query_and_print(conn, "SELECT * FROM archived_results ORDER BY result_id;")

    # Re-seed archived_results because we still need it later
    exec_sql(conn, """
    INSERT INTO archived_results (result_id, order_id, test_name, value, unit, flag, performed_at, doctor_reviewed_by) VALUES
    (7001,  999, 'BUN',        19.20, 'mg/dL', 'normal', '2026-01-01 09:00:00', NULL),
    (7002,  999, 'Creatinine',  0.80, 'mg/dL', 'normal', '2026-01-01 09:00:00', 'Dr. Kim');
    """)
    print("Re-inserted archived_results rows ✅")

    # --- DROP: remove the table definition completely
    banner("3C) DROP (remove table, then recreate)")
    exec_sql(conn, "DROP TABLE archived_results;")
    print("Dropped archived_results table ✅")

    # Recreate dropped table so rest of demos work
    exec_sql(conn, """
    CREATE TABLE archived_results (
      result_id     INT PRIMARY KEY,
      order_id      INT NOT NULL,
      test_name     TEXT NOT NULL,
      value         NUMERIC(10,2),
      unit          TEXT,
      flag          TEXT,
      performed_at  TIMESTAMP NOT NULL,
      doctor_reviewed_by TEXT NULL
    );
    """)
    print("Recreated archived_results table ✅")

    # Reinsert data again
    exec_sql(conn, """
    INSERT INTO archived_results (result_id, order_id, test_name, value, unit, flag, performed_at, doctor_reviewed_by) VALUES
    (7001,  999, 'BUN',        19.20, 'mg/dL', 'normal', '2026-01-01 09:00:00', NULL),
    (7002,  999, 'Creatinine',  0.80, 'mg/dL', 'normal', '2026-01-01 09:00:00', 'Dr. Kim');
    """)
    print("Re-seeded archived_results ✅")


# ------------------------------------------------------------
# 5) UNION vs UNION ALL
# ------------------------------------------------------------
def union_demo(conn) -> None:
    banner("4) UNION vs UNION ALL")

    banner("4A) UNION (removes duplicates)")
    query_and_print(conn, """
    SELECT test_name FROM results
    UNION
    SELECT test_name FROM archived_results
    ORDER BY test_name;
    """)

    banner("4B) UNION ALL (keeps duplicates)")
    query_and_print(conn, """
    SELECT test_name FROM results
    UNION ALL
    SELECT test_name FROM archived_results
    ORDER BY test_name;
    """)


# ------------------------------------------------------------
# 6) INNER JOIN vs LEFT JOIN
# ------------------------------------------------------------
def join_demo(conn) -> None:
    banner("5) INNER JOIN vs LEFT JOIN")

    banner("5A) INNER JOIN (only matching)")
    query_and_print(conn, """
    SELECT o.order_id, o.patient_id, r.result_id, r.test_name, r.value, r.flag
    FROM orders o
    INNER JOIN results r ON r.order_id = o.order_id
    ORDER BY o.order_id, r.result_id;
    """)

    banner("5B) LEFT JOIN (keep all from left side)")
    query_and_print(conn, """
    SELECT o.order_id, o.patient_id, r.result_id, r.test_name
    FROM orders o
    LEFT JOIN results r ON r.order_id = o.order_id
    ORDER BY o.order_id, r.result_id;
    """)

    banner("5C) LEFT JOIN + WHERE ... IS NULL (find orders with NO results)")
    query_and_print(conn, """
    SELECT o.order_id, o.patient_id
    FROM orders o
    LEFT JOIN results r ON r.order_id = o.order_id
    WHERE r.result_id IS NULL
    ORDER BY o.order_id;
    """)


# ------------------------------------------------------------
# 7) WHERE vs HAVING
# ------------------------------------------------------------
def where_having_demo(conn) -> None:
    banner("6) WHERE vs HAVING")

    banner("6A) WHERE filters BEFORE GROUP BY")
    query_and_print(conn, """
    SELECT test_name, COUNT(*) AS cnt
    FROM results
    WHERE flag = 'normal'
    GROUP BY test_name
    ORDER BY cnt DESC, test_name;
    """)

    banner("6B) HAVING filters AFTER GROUP BY")
    query_and_print(conn, """
    SELECT test_name, COUNT(*) AS cnt
    FROM results
    GROUP BY test_name
    HAVING COUNT(*) >= 2
    ORDER BY cnt DESC, test_name;
    """)


# ------------------------------------------------------------
# 8) NULL checks
# ------------------------------------------------------------
def null_demo(conn) -> None:
    banner("7) NULL (IS NULL / IS NOT NULL)")

    banner("7A) doctor_reviewed_by IS NULL")
    query_and_print(conn, """
    SELECT result_id, test_name, doctor_reviewed_by
    FROM results
    WHERE doctor_reviewed_by IS NULL
    ORDER BY result_id;
    """)

    banner("7B) doctor_reviewed_by IS NOT NULL")
    query_and_print(conn, """
    SELECT result_id, test_name, doctor_reviewed_by
    FROM results
    WHERE doctor_reviewed_by IS NOT NULL
    ORDER BY result_id;
    """)


# ------------------------------------------------------------
# 9) Index + EXPLAIN ANALYZE
# ------------------------------------------------------------
def index_demo(conn) -> None:
    banner("8) INDEX + EXPLAIN ANALYZE")

    banner("8A) EXPLAIN ANALYZE before index")
    query_and_print(conn, """
    EXPLAIN ANALYZE
    SELECT * FROM results WHERE order_id = 1003;
    """, limit=None)

    banner("8B) Create index on results(order_id)")
    exec_sql(conn, "CREATE INDEX IF NOT EXISTS idx_results_order_id ON results(order_id);")
    print("Index created ✅ (idx_results_order_id)")

    banner("8C) EXPLAIN ANALYZE after index")
    query_and_print(conn, """
    EXPLAIN ANALYZE
    SELECT * FROM results WHERE order_id = 1003;
    """, limit=None)


# ------------------------------------------------------------
# 10) Compare two tables (diff examples)
# ------------------------------------------------------------
def compare_tables_demo(conn) -> None:
    banner("9) TWO TABLE COMPARISON (results vs archived_results)")

    banner("9A) test_name in results but NOT in archived_results")
    query_and_print(conn, """
    SELECT DISTINCT r.test_name
    FROM results r
    LEFT JOIN archived_results a ON a.test_name = r.test_name
    WHERE a.test_name IS NULL
    ORDER BY r.test_name;
    """)

    banner("9B) test_name in archived_results but NOT in results")
    query_and_print(conn, """
    SELECT DISTINCT a.test_name
    FROM archived_results a
    LEFT JOIN results r ON r.test_name = a.test_name
    WHERE r.test_name IS NULL
    ORDER BY a.test_name;
    """)

    banner("9C) Same test_name exists in both but VALUE differs (IS DISTINCT FROM handles NULL safely)")
    query_and_print(conn, """
    SELECT
      r.test_name,
      r.value AS current_value,
      a.value AS archived_value
    FROM results r
    JOIN archived_results a ON a.test_name = r.test_name
    WHERE r.value IS DISTINCT FROM a.value
    ORDER BY r.test_name;
    """)


# ------------------------------------------------------------
# Main execution order (IMPORTANT: keep sequence)
# ------------------------------------------------------------
if __name__ == "__main__":
    banner("CONNECTING TO POSTGRES")
    with engine.connect() as conn:
        print("Connected ✅")

        # ✅ Use an explicit transaction so changes are committed as a unit
        with conn.begin():  # Transaction begins here
            reset_schema(conn)           # 0) drop old tables
            create_tables(conn)          # 1) create tables
            seed_data(conn)              # 2) insert data
            delete_truncate_drop_demo(conn)  # 3) delete/truncate/drop + recreate
            union_demo(conn)             # 4) union examples
            join_demo(conn)              # 5) join examples
            where_having_demo(conn)      # 6) where vs having
            null_demo(conn)              # 7) null handling
            index_demo(conn)             # 8) index + explain analyze
            compare_tables_demo(conn)    # 9) compare tables / diff

        banner("DONE ✅ All demos executed in order")
