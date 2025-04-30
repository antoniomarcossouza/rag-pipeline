from datetime import datetime

import arxiv
from langchain_ollama import OllamaEmbeddings
from langchain_postgres import Column, PGEngine, PGVectorStore

from .sql import DatabaseConnection


def process_paper(result: arxiv.Result):
    return {
        "pdf_url": result.pdf_url,
        "title": result.title,
        "authors": [author.name for author in result.authors],
        "summary": result.summary,
        "published": result.published.isoformat(),
        "updated": result.updated.isoformat(),
    }


def get_arxiv_papers(query: str, max_results: int) -> list:
    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=max_results)
    results = client.results(search)

    return [process_paper(result) for result in results]


def get_insert_papers_query(papers: list) -> str:
    template = (
        "    ('{url}', E'{title}', E'{authors}', E'{summary}', "
        "'{published}', '{updated}'),"
    )
    values = "\n".join(
        [
            template.format_map(
                {
                    "url": paper["pdf_url"],
                    "title": paper["title"].replace("'", ""),
                    "authors": ", ".join(paper["authors"]).replace("'", ""),
                    "summary": paper["summary"].replace("'", ""),
                    "published": paper["published"],
                    "updated": paper["updated"],
                }
            )
            for paper in papers
        ]
    )

    query = f"""INSERT INTO tbl_documents (
    pdf_url,
    title,
    authors,
    summary,
    published,
    updated
) VALUES
{values[:-1]};
"""

    return query


def arxiv_etl(
    db: DatabaseConnection,
    subject: str,
    results: int,
) -> None:
    db.action_query(
        query=get_insert_papers_query(get_arxiv_papers(subject, results))
    )


async def init_arxiv_vectorstore_table(engine: PGEngine) -> None:
    await engine.ainit_vectorstore_table(
        table_name="tbl_document_chunks",
        vector_size=2048,
        metadata_columns=[
            Column("doc_id", "INTEGER"),
            Column("created_at", "TIMESTAMP"),
        ],
    )


async def create_arxiv_vectorstore(engine: PGEngine) -> PGVectorStore:
    return await PGVectorStore.create(
        engine=engine,
        embedding_service=OllamaEmbeddings(model="llama3.2:1b"),
        table_name="tbl_document_chunks",
        metadata_columns=["doc_id", "created_at"],
    )


def treat_arxiv_metadata(metadata: dict, record_id: int) -> dict:
    return {
        "doc_id": record_id,
        "page": metadata["page"],
        "total_pages": metadata["total_pages"],
        "created_at": datetime.fromisoformat(metadata["creationdate"]).replace(
            tzinfo=None
        ),
    }
