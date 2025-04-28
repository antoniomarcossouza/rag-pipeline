from io import BytesIO

import arxiv
import httpx
import pymupdf


def get_pdf_text(pdf_url: str) -> str:
    response = httpx.get(pdf_url)
    pdf_data = BytesIO(response.content)
    doc = pymupdf.open(stream=pdf_data, filetype="pdf")

    full_text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        full_text += page.get_text()

    return full_text


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
        "    ('{url}', E'{title}', ARRAY{authors}, E'{summary}', "
        "'{published}', '{updated}'),"
    )
    values = "\n".join(
        [
            template.format_map(
                {
                    "url": paper["pdf_url"],
                    "title": paper["title"].replace("'", "''"),
                    "authors": paper["authors"],
                    "summary": paper["summary"].replace("'", "''"),
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
