from utils.arxiv import get_arxiv_papers, get_insert_papers_query
from utils.sql import action_query, select_query

QUERY = "machine learning"
MAX_RESULTS = 2000


if __name__ == "__main__":
    papers = get_arxiv_papers(QUERY, MAX_RESULTS)

    action_query(query=get_insert_papers_query(papers))

    items = select_query(
        """
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
"""
    )

    print(items)
