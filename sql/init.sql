CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE tbl_documents (
    id bigserial PRIMARY KEY,
    pdf_url text,
    title text,
    authors text,
    summary text,
    published timestamp,
    updated timestamp,
    created_at timestamp default now()
);