import psycopg2

CONNECTION = psycopg2.connect(
    database="vectordb",
    user="username",
    password="password",
    host="127.0.0.1",
    port="5432",
)


def action_query(
    query: str,
    conn: psycopg2.extensions.connection = CONNECTION,
) -> None:
    with conn.cursor() as cur:
        try:
            cur.execute(query)
            conn.commit()
        except psycopg2.DatabaseError as e:
            print(f"Error {e}")
            conn.rollback()


def select_query(
    query: str,
    conn: psycopg2.extensions.connection = CONNECTION,
) -> list:
    with conn.cursor() as cur:
        try:
            cur.execute(query)
            return cur.fetchall()
        except psycopg2.DatabaseError as e:
            print(f"Error {e}")
            return None
