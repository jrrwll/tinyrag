
create table file (
    id         bigint     not null primary key,
    created_at timestamp    not null default current_timestamp,
    type       varchar(50)  not null,
    name       varchar(100) not null,
    size       bigint       not null,
    mime_type  varchar(100) not null
) default charset utf8mb4;

create table knowledge (
    id              bigint     not null primary key,
    created_at      timestamp    not null default current_timestamp,
    updated_at      timestamp    not null default current_timestamp on update current_timestamp,
    deleted         tinyint      not null default 0,
    name            varchar(100) not null,
    description     varchar(1000)         default null,
    enable          tinyint      not null default 1,
    process_rule    text,
    embedding_model text,
    retrieval_model text
) default charset utf8mb4;

create table knowledge_document (
    id           bigint  not null primary key,
    created_at   timestamp not null default current_timestamp,
    updated_at   timestamp not null default current_timestamp on update current_timestamp,
    deleted      tinyint   not null default 0,
    knowledge_id bigint  not null,
    position     int       not null,
    word_count   int                default 0,
    source_type  varchar(32),
    source_info  text,
    indexing     tinyint   not null default 0
) default charset utf8mb4;

create table knowledge_document_chunk (
    id           varchar(100)      not null primary key,
    created_at   timestamp     not null default current_timestamp,
    updated_at   timestamp     not null default current_timestamp on update current_timestamp,
    deleted      tinyint       not null default 0,
    knowledge_id bigint      not null,
    document_id  bigint      not null,
    position     int           not null,
    content      varchar(1024) not null,
    word_count   int                    default 0,
    keywords     text,
    index_doc_id varchar(100)  null     default null
) default charset utf8mb4;
