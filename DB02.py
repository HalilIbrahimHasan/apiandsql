from sqlalchemy import create_engine, text

engine = create_engine("postgresql+psycopg2://selma:SIFREN@localhost:5432/postgres")

with engine.begin() as conn:  # ✅ AUTO-COMMIT
    # conn.execute(text("""
    #     CREATE TABLE IF NOT EXISTS public.students (
    #         id SERIAL PRIMARY KEY,
    #         name VARCHAR(50),
    #         lastname VARCHAR(50),
    #         age INT,
    #         grade VARCHAR(10),
    #         major VARCHAR(100)
    #     );
    # """))

    # conn.execute(text("TRUNCATE public.students RESTART IDENTITY;"))

    conn.execute(text("""
    INSERT INTO public.students (name, lastname, age, grade, major) VALUES
    ('James', 'Miller', 25, 'B', 'Mechanical Engineering'),
    ('Olivia', 'Garcia', 21, 'A', 'Biotechnology'),
    ('William', 'Harris', 22, 'C', 'Finance'),
    ('Isabella', 'Martinez', 20, 'B', 'Psychology'),
    ('Benjamin', 'Lopez', 23, 'A', 'Information Systems'),
    ('Mia', 'Gonzalez', 19, 'A', 'Neuroscience'),
    ('Alexander', 'Perez', 24, 'B', 'Civil Engineering'),
    ('Charlotte', 'Kim', 22, 'A', 'Statistics'),
    ('Ethan', 'Nguyen', 21, 'C', 'International Relations'),
    ('Ava', 'Patel', 20, 'B', 'Health Informatics');
"""))


with engine.connect() as conn:
    rows = conn.execute(text("SELECT * FROM public.students ORDER BY id;")).fetchall()
    print("row_count:", len(rows))
    print(rows[:3])
