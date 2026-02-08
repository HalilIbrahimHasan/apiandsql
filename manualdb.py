from sqlalchemy import create_engine, text

# ✅ Update your DB URL
DB_URL = "postgresql+psycopg2://selma:1234@localhost:5432/postgres"

engine = create_engine(DB_URL, future=True)



# ------------------------------------------------------------
# Helper: runs SQL that does NOT return rows (CREATE/INSERT/DELETE...)
# ------------------------------------------------------------
def run_exec(conn, sql):
    print("\n--- Running SQL ---")
    print(sql.strip())
    conn.execute(text(sql))
    print("✅ Done")


# ------------------------------------------------------------
# Helper: runs SELECT and prints rows
# ------------------------------------------------------------
def run_select(conn, sql):
    print("\n--- Running SQL ---")
    print(sql.strip())
    result = conn.execute(text(sql))
    rows = result.fetchall()

    print(f"Rows: {len(rows)}")
    for row in rows:
        print(row)


# ============================================================
# STEP 1) DROP TABLES (RESET)
# ============================================================
def step_1_drop_tables(conn):
    run_exec(conn, "DROP TABLE IF EXISTS archived_results;")
    run_exec(conn, "DROP TABLE IF EXISTS results;")
    run_exec(conn, "DROP TABLE IF EXISTS orders;")


# ============================================================
# STEP 2) CREATE TABLES
# ============================================================
def step_2_create_tables(conn):
    run_exec(conn, """
    CREATE TABLE orders (
      order_id      INT PRIMARY KEY,
      patient_id    INT NOT NULL,
      ordered_at    TIMESTAMP NOT NULL DEFAULT now(),
      status        TEXT NOT NULL
    );
    """)

    run_exec(conn, """
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

    run_exec(conn, """
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


# ============================================================
# STEP 3) INSERT SAMPLE DATA
# ============================================================
def step_3_insert_data(conn):
    run_exec(conn, """
    INSERT INTO orders (order_id, patient_id, ordered_at, status) VALUES
    (1001, 1009, '2026-02-07 00:10:00', 'published'),
    (1002, 1010, '2026-02-07 00:12:00', 'draft'),
    (1003, 1009, '2026-02-07 00:24:43', 'published');
    """)

    run_exec(conn, """
    INSERT INTO results (result_id, order_id, test_name, value, unit, flag, performed_at, doctor_reviewed_by) VALUES
    (8001, 1001, 'Glucose (fasting)', 92.00, 'mg/dL', 'normal', '2026-02-07 00:10:30', NULL),
    (8002, 1003, 'BUN', 18.90, 'mg/dL', 'normal', '2026-02-07 00:24:43', NULL),
    (8003, 1003, 'Creatinine',0.72, 'mg/dL', 'normal', '2026-02-07 00:24:43', NULL),
    (8004, 1002, 'HbA1c', 6.10, '%',     'high',   '2026-02-07 00:12:20', 'Dr. Lee');
    """)

    run_exec(conn, """
    INSERT INTO archived_results (result_id, order_id, test_name, value, unit, flag, performed_at, doctor_reviewed_by) VALUES
    (7001,  999, 'BUN',        19.20, 'mg/dL', 'normal', '2026-01-01 09:00:00', NULL),
    (7002,  999, 'Creatinine',  0.80, 'mg/dL', 'normal', '2026-01-01 09:00:00', 'Dr. Kim');
    """)


# ============================================================
# STEP 4) SHOW TABLE DATA
# ============================================================
def step_4_show_data(conn):
    run_select(conn, "SELECT * FROM orders ORDER BY order_id;")
    run_select(conn, "SELECT * FROM results ORDER BY result_id;")
    run_select(conn, "SELECT * FROM archived_results ORDER BY result_id;")


# ============================================================
# STEP 5) DELETE example
# ============================================================
def step_5_delete_example(conn):
    run_exec(conn, "DELETE FROM results WHERE result_id = 8001;")
    run_select(conn, "SELECT result_id, test_name FROM results ORDER BY result_id;")


# ============================================================
# STEP 6) TRUNCATE example
# ============================================================
def step_6_truncate_example(conn):
    run_exec(conn, "TRUNCATE TABLE archived_results;")
    run_select(conn, "SELECT * FROM archived_results;")


# ============================================================
# STEP 7) DROP + Recreate archived_results
# ============================================================
def step_7_drop_and_recreate_archived(conn):
    run_exec(conn, "DROP TABLE IF EXISTS archived_results;")

    run_exec(conn, """
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

    print("✅ archived_results dropped and recreated")


# ============================================================
# STEP 8) UNION vs UNION ALL
# ============================================================
def step_8_union_examples(conn):
    run_select(conn, """
    SELECT test_name FROM results
    UNION
    SELECT test_name FROM archived_results
    ORDER BY test_name;
    """)

    run_select(conn, """
    SELECT test_name FROM results
    UNION ALL
    SELECT test_name FROM archived_results
    ORDER BY test_name;
    """)


# ============================================================
# STEP 9) JOIN examples
# ============================================================
def step_9_join_examples(conn):
    run_select(conn, """
    SELECT o.order_id, o.patient_id, r.test_name, r.value
    FROM orders o
    INNER JOIN results r ON r.order_id = o.order_id
    ORDER BY o.order_id;
    """)

    run_select(conn, """
    SELECT o.order_id, o.patient_id, r.test_name
    FROM orders o
    LEFT JOIN results r ON r.order_id = o.order_id
    ORDER BY o.order_id;
    """)


# ============================================================
# STEP 10) WHERE vs HAVING
# ============================================================
def step_10_where_having(conn):
    run_select(conn, """
    SELECT test_name, COUNT(*) AS cnt
    FROM results
    WHERE flag = 'normal'
    GROUP BY test_name
    ORDER BY cnt DESC;
    """)

    run_select(conn, """
    SELECT test_name, COUNT(*) AS cnt
    FROM results
    GROUP BY test_name
    HAVING COUNT(*) >= 2
    ORDER BY cnt DESC;
    """)


# ============================================================
# STEP 11) NULL examples
# ============================================================
def step_11_null_examples(conn):
    run_select(conn, """
    SELECT result_id, test_name, doctor_reviewed_by
    FROM results
    WHERE doctor_reviewed_by IS NULL
    ORDER BY result_id;
    """)

    run_select(conn, """
    SELECT result_id, test_name, doctor_reviewed_by
    FROM results
    WHERE doctor_reviewed_by IS NOT NULL
    ORDER BY result_id;
    """)


# ============================================================
# STEP 12) Index + Explain
# ============================================================
def step_12_index_explain(conn):
    run_select(conn, "EXPLAIN ANALYZE SELECT * FROM results WHERE order_id = 1003;")
    run_exec(conn, "CREATE INDEX IF NOT EXISTS idx_results_order_id ON results(order_id);")
    run_select(conn, "EXPLAIN ANALYZE SELECT * FROM results WHERE order_id = 1003;")


# ============================================================
# STEP 13) Compare two tables (differences)
# ============================================================
def step_13_compare_tables(conn):
    run_select(conn, """
    SELECT DISTINCT r.test_name
    FROM results r
    LEFT JOIN archived_results a ON a.test_name = r.test_name
    WHERE a.test_name IS NULL
    ORDER BY r.test_name;
    """)

    run_select(conn, """
    SELECT DISTINCT a.test_name
    FROM archived_results a
    LEFT JOIN results r ON r.test_name = a.test_name
    WHERE r.test_name IS NULL
    ORDER BY a.test_name;
    """)


# ============================================================
# MENU (Run one by one)
# ============================================================
MENU = """
Choose a step:
  1  - Drop tables (reset)
  2  - Create tables
  3  - Insert sample data
  4  - Show all data
  5  - DELETE example
  6  - TRUNCATE example
  7  - DROP + Recreate archived_results
  8  - UNION vs UNION ALL
  9  - JOIN examples
  10 - WHERE vs HAVING
  11 - NULL examples
  12 - INDEX + EXPLAIN
  13 - Compare two tables
  0  - Exit
"""


def main():
    with engine.connect() as conn:

    

        # ✅ Transaction: all steps commit together
        with conn.begin():
            print("Connected ✅")



          


            # step_3_insert_data(conn)

            # run_select(conn, """ SELECT * FROM orders; """)

            # run_select(conn, """ SELECT * FROM results; """)

            # run_select(conn, """ 
            # SELECT o.order_id, o.patient_id, r.test_name, r.value, r.flag
            # FROM orders o
            # INNER JOIN results r ON r.order_id = o.order_id
            # ORDER BY o.order_id, r.result_id;
            #     """)

            # run_exec(conn, """ DELETE FROM results
            #     WHERE result_id = 8001; """)

            

            
            

            # run_select(conn, """ SELECT * FROM archived_results; """)

            # --- Setup (recommended first run) ---
            # step_1_drop_tables(conn)
            # step_2_create_tables(conn)
            # step_3_insert_data(conn)
            # step_4_show_data(conn)

            # --- Demo queries ---
            # step_5_delete_example(conn)
            # step_6_truncate_example(conn)
            step_7_drop_and_recreate_archived(conn)

            # step_8_union_examples(conn)
            # step_9_join_examples(conn)
            # step_10_where_having(conn)
            # step_11_null_examples(conn)

            # step_12_index_explain(conn)
            # step_13_compare_tables(conn)


if __name__ == "__main__":
    main()
