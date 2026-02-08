from sqlalchemy import create_engine

# ✅ Update password
DB_URL = "postgresql+psycopg2://selma:1234@localhost:5432/postgres"

engine = create_engine(DB_URL, future=True)

if __name__ == "__main__":
    with engine.connect() as conn:
        print("Connected ✅")
