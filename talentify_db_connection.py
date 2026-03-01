from sqlalchemy import create_engine, inspect

DB_URL = "postgresql+psycopg2://talentifyhealth_user:yMFFb4CgLkDCotG7qw4MGzMBY2tAonzO@dpg-d67tn60gjchc73b7cjvg-a.oregon-postgres.render.com:5432/talentifyhealth"

def main():
    engine = create_engine(DB_URL, connect_args={"sslmode": "require"})

    inspector = inspect(engine)
    tables = inspector.get_table_names(schema="public")

    print("Tables:")
    for t in tables:
        print("-", t)

if __name__ == "__main__":
    main()
