from sqlalchemy import text
from db_connection import engine

def insert_two_students():
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO public.students (name, lastname, age, grade, major) VALUES
            ('Noah', 'Adams', 22, 'B', 'Statistics'),
            ('Lily', 'Turner', 20, 'A', 'Economics');
        """))
    print("✅ Inserted 2 students")

def select_all():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM public.students ORDER BY id;")).fetchall()
        print(f"Rows: {len(rows)}")
        for r in rows:
            print(r)

def filters_examples():
    with engine.connect() as conn:
        print("\n-- age > 21")
        print(conn.execute(text("SELECT * FROM public.students WHERE age > 21 ORDER BY age;")).fetchall())

        print("\n-- grade = 'A'")
        print(conn.execute(text("SELECT * FROM public.students WHERE grade = 'A' ORDER BY id;")).fetchall())

        print("\n-- ORDER BY lastname DESC LIMIT 3")
        print(conn.execute(text("SELECT * FROM public.students ORDER BY lastname DESC LIMIT 3;")).fetchall())

        print("\n-- LIKE name starts with 'A'")
        print(conn.execute(text("SELECT * FROM public.students WHERE name LIKE 'A%';")).fetchall())

        print("\n-- BETWEEN age 20 and 22")
        print(conn.execute(text("SELECT * FROM public.students WHERE age BETWEEN 20 AND 22 ORDER BY age;")).fetchall())

if __name__ == "__main__":
    insert_two_students()
    select_all()
    filters_examples()
