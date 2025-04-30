import psycopg2
from langchain_postgres import PGEngine


class DatabaseConnection:
    def __init__(self, db_name, user, password, host, port):
        self.connection = psycopg2.connect(
            database=db_name,
            user=user,
            password=password,
            host=host,
            port=port,
        )
        self.langchain_engine = PGEngine.from_connection_string(
            url=(
                f"postgresql+asyncpg://{user}:{password}@{host}"
                f":{port}/{db_name}"
            )
        )

    def action_query(
        self,
        query: str,
    ) -> None:
        with self.connection.cursor() as cur:
            try:
                cur.execute(query)
                self.connection.commit()
            except psycopg2.DatabaseError as e:
                print(f"Error {e}")
                self.connection.rollback()

    def select_query(
        self,
        query: str,
    ) -> list:
        with self.connection.cursor() as cur:
            try:
                cur.execute(query)
                return cur.fetchall()
            except psycopg2.DatabaseError as e:
                print(f"Error {e}")
                return None
