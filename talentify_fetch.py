from sqlalchemy import create_engine, text

DB_URL = "postgresql+psycopg2://talentifyhealth_user:yMFFb4CgLkDCotG7qw4MGzMBY2tAonzO@dpg-d67tn60gjchc73b7cjvg-a.oregon-postgres.render.com:5432/talentifyhealth"

def get_engine():
    return create_engine(DB_URL, connect_args={"sslmode": "require"}, pool_pre_ping=True)

def fetch_patient_profiles(engine, limit=20):
    sql = text("""
        SELECT *
        FROM public.patient_profiles
        ORDER BY 1 DESC
        LIMIT :limit;
    """)
    with engine.connect() as conn:
        return conn.execute(sql, {"limit": limit}).mappings().all()

def fetch_test_orders(engine, limit=20):
    sql = text("""
        SELECT *
        FROM public.test_orders
        ORDER BY 1 DESC
        LIMIT :limit;
    """)
    with engine.connect() as conn:
        return conn.execute(sql, {"limit": limit}).mappings().all()

def main():
    engine = get_engine()

    patients = fetch_patient_profiles(engine, limit=20)
    orders = fetch_test_orders(engine, limit=20)

    print("\n✅ patient_profiles rows:", len(patients))
    for row in patients[:5]:
        print(row)

    print("\n✅ test_orders rows:", len(orders))
    for row in orders[:5]:
        print(row)

if __name__ == "__main__":
    main()
