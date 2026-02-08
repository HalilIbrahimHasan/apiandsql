from sqlalchemy import create_engine, text

# 🔐 CONNECTION
engine = create_engine(
    "postgresql+psycopg2://selma:1234@localhost:5432/postgres"
)

with engine.connect() as conn:
    print("🎉 Connected with SQLAlchemy!")

    # 🔥 DROP TABLE if exists (temiz başlamak için)
    conn.execute(text("DROP TABLE IF EXISTS students;"))

    # 🌟 CREATE TABLE
    create_table_sql = """
    CREATE TABLE students (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50),
        lastname VARCHAR(50),
        age INT,
        grade VARCHAR(10),
        major VARCHAR(100)
    );
    """
    conn.execute(text(create_table_sql))
    print("✅ students table created")

    # 🌟 INSERT 10 RECORDS
    insert_sql = """
    INSERT INTO students (name, lastname, age, grade, major) VALUES
    ('John', 'Smith', 20, 'A', 'Computer Science'),
    ('Emily', 'Brown', 22, 'B', 'Data Science'),
    ('Michael', 'Johnson', 19, 'A', 'Engineering'),
    ('Sarah', 'Wilson', 21, 'C', 'Business'),
    ('David', 'Lee', 23, 'B', 'Cyber Security'),
    ('Anna', 'Taylor', 20, 'A', 'Mathematics'),
    ('Robert', 'Anderson', 24, 'B', 'Physics'),
    ('Laura', 'Martin', 22, 'A', 'Software Engineering'),
    ('Daniel', 'Clark', 21, 'C', 'Economics'),
    ('Sophia', 'Moore', 19, 'A', 'Artificial Intelligence');
    """
    conn.execute(text(insert_sql))
    print("✅ 10 students inserted")

    # 🌟 SELECT & PRINT
    result = conn.execute(text("SELECT * FROM students;"))
    print("\n📋 STUDENTS TABLE:")
    for row in result:
        print(row)
