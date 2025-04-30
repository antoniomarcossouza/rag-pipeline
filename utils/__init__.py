from pathlib import Path

import httpx
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from utils.arxiv import treat_arxiv_metadata


def write_web_content_to_file(url: str, filepath: Path) -> None:
    with httpx.stream("GET", url) as response:
        response.raise_for_status()
        with filepath.open("wb") as f:
            for chunk in response.iter_bytes():
                f.write(chunk)


def split_document(filepath: Path, doc_id: int) -> list[Document]:
    doc = PyPDFLoader(filepath).load()
    split = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    ).split_documents(doc)

    return [
        Document(
            page_content=doc.page_content,
            metadata=treat_arxiv_metadata(
                metadata=doc.metadata,
                record_id=doc_id,
            ),
        )
        for doc in split
    ]
