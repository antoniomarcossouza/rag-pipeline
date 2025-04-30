from utils.arxiv import get_arxiv_papers, get_insert_papers_query
from utils.sql import action_query

QUERY = "machine learning"
MAX_RESULTS = 1000


if __name__ == "__main__":
    papers = get_arxiv_papers(QUERY, MAX_RESULTS)

    action_query(query=get_insert_papers_query(papers))
