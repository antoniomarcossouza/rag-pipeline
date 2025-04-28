CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE tbl_documents (
    id bigserial PRIMARY KEY,
    pdf_url varchar(256),
    title varchar(256),
    authors varchar(256)[],
    summary text,
    published timestamp,
    updated timestamp,
    created_at timestamp default now()
);

CREATE TABLE tbl_document_chunks (
    id bigserial PRIMARY KEY,
    doc_id bigserial not null references tbl_documents(id),
    chunk JSONB,       
    embedding vector(384),
    created_at timestamp default now()
);

CREATE INDEX ON t_document_chunks USING hnsw (embedding vector_ip_ops) WITH (m = 16, ef_construction = 128);