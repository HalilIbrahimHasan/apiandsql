from sqlalchemy import text
from db_connection import engine

def counts_and_distinct():
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM public.students;")).scalar_one()
        a_count = conn.execute(text("SELECT COUNT(*) FROM public.students WHERE grade='A';")).scalar_one()
        print("Total students:", total)
        print("Grade A count:", a_count)

        print("\nDistinct majors:")
        print(conn.execute(text("SELECT DISTINCT major FROM public.students ORDER BY major;")).fetchall())

        print("\nDistinct grades:")
        print(conn.execute(text("SELECT DISTINCT grade FROM public.students ORDER BY grade;")).fetchall())

def groupby_and_having():
    with engine.connect() as conn:
        print("\nStudents per major:")
        print(conn.execute(text("""
            SELECT major, COUNT(*) AS cnt
            FROM public.students
            GROUP BY major
            ORDER BY cnt DESC, major;
        """)).fetchall())

        print("\nAvg age per grade:")
        print(conn.execute(text("""
            SELECT grade, AVG(age) AS avg_age
            FROM public.students
            GROUP BY grade
            ORDER BY grade;
        """)).fetchall())

        print("\nMajors with more than 1 student (HAVING):")
        print(conn.execute(text("""
            SELECT major, COUNT(*) AS cnt
            FROM public.students
            GROUP BY major
            HAVING COUNT(*) > 1
            ORDER BY cnt DESC;
        """)).fetchall())

if __name__ == "__main__":
    counts_and_distinct()
    groupby_and_having()
