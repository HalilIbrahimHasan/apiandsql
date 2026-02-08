from sqlalchemy import text
from db_connection import engine

def update_examples():
    with engine.begin() as conn:
        # Example 1: set grade for a specific name
        conn.execute(text("UPDATE public.students SET grade = 'A' WHERE name = 'James';"))

        # Example 2: age + 1 for a major
        conn.execute(text("UPDATE public.students SET age = age + 1 WHERE major = 'Statistics';"))

    print("✅ Updates done")

def delete_examples():
    with engine.begin() as conn:
        # Example 1: delete by lastname
        conn.execute(text("DELETE FROM public.students WHERE lastname = 'Smith';"))

        # Example 2: delete by age condition
        conn.execute(text("DELETE FROM public.students WHERE age < 19;"))

    print("✅ Deletes done")

def preview():
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT id, name, lastname, age, grade, major FROM public.students ORDER BY id;")).fetchall()
        for r in rows:
            print(r)

if __name__ == "__main__":
    update_examples()
    delete_examples()
    preview()
