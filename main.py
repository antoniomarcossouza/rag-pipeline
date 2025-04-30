import asyncio
import tempfile
from pathlib import Path

from utils import split_document, write_web_content_to_file
from utils.arxiv import (
    arxiv_etl,
    create_arxiv_vectorstore,
)
from utils.sql import DatabaseConnection

POSTGRES_USER = "username"
POSTGRES_PASSWORD = "password"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_DB = "vectordb"

QUERY = "machine learning"
MAX_RESULTS = 1000


if __name__ == "__main__":

    db = DatabaseConnection(
        db_name=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
    )

    arxiv_etl(db=db, subject=QUERY, results=MAX_RESULTS)

    vectorstore = asyncio.run(create_arxiv_vectorstore(db.langchain_engine))

    items = db.select_query(
        query="""
    with ranked as (
        select
            *,
            dense_rank() over (
                partition by pdf_url
                order by created_at desc
            ) as rnk
        from tbl_documents
    )

    select
        id,
        pdf_url
    from ranked
    where rnk = 1
    """,
    )

    tmp_dir = Path(tempfile.gettempdir()).resolve()
    for doc_id, pdf_url in items:
        save_path = tmp_dir / pdf_url.split("/")[-1]

        write_web_content_to_file(pdf_url, save_path)
        split = split_document(save_path, doc_id)

        vectorstore.add_documents(split)
