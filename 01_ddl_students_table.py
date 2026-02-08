from sqlalchemy import text
from db_connection import engine  # or copy DB_URL + engine here

def create_table():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS public.students (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50),
                lastname VARCHAR(50),
                age INT,
                grade VARCHAR(10),
                major VARCHAR(100)
            );
        """))
    print("✅ Table ensured: public.students")

def add_columns():
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE public.students ADD COLUMN IF NOT EXISTS gpa FLOAT;"))
        conn.execute(text("ALTER TABLE public.students ADD COLUMN IF NOT EXISTS enrollment_year INT;"))
    print("✅ Columns added if missing: gpa, enrollment_year")

def drop_columns():
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE public.students DROP COLUMN IF EXISTS gpa;"))
        conn.execute(text("ALTER TABLE public.students DROP COLUMN IF EXISTS enrollment_year;"))
    print("✅ Columns dropped if existed: gpa, enrollment_year")

def truncate_table(restart_identity=True):
    sql = "TRUNCATE public.students RESTART IDENTITY;" if restart_identity else "TRUNCATE public.students;"
    with engine.begin() as conn:
        conn.execute(text(sql))
    print(f"✅ Truncated students (restart_identity={restart_identity})")

if __name__ == "__main__":
    create_table()
    # add_columns()
    # drop_columns()
    # truncate_table(restart_identity=True)


add_columns()

drop_columns()