create table file (
    id           char(36)     not null primary key,
    created_at   timestamp    not null default current_timestamp,
    tenant_id    bigint       not null,
    workspace_id bigint       not null,
    type         varchar(50)  not null,
    name         varchar(100) not null,
    size         bigint       not null,
    mime_type    varchar(100) not null
) default charset utf8mb4;

create table knowledge (
    id                     bigint       not null auto_increment primary key,
    created_at             timestamp    not null default current_timestamp,
    updated_at             timestamp    not null default current_timestamp on update current_timestamp,
    deleted                tinyint      not null default 0,
    tenant_id              bigint       not null,
    workspace_id           bigint       not null,
    name                   varchar(100) not null,
    description            varchar(1000)         default null,
    enable                 tinyint      not null default 1,
    process_rule           text,
    llm_model_config       text,
    embedding_model_config text,
    vector_store_config    text,
    retrieval_model_config text
) default charset utf8mb4;

create table knowledge_document (
    id           varchar(100) not null primary key,
    created_at   timestamp    not null default current_timestamp,
    tenant_id    bigint       not null,
    workspace_id bigint       not null,
    knowledge_id bigint       not null,
    position     int          not null,
    word_count   int                   default 0,
    source_type  varchar(32),
    source_info  text,
    indexing     tinyint      not null default 0,
    index idx_tenant_id_knowledge_id (tenant_id, knowledge_id)
) default charset utf8mb4;

create table knowledge_document_chunk (
    id           varchar(100)  not null primary key,
    created_at   timestamp     not null default current_timestamp,
    tenant_id    bigint        not null,
    workspace_id bigint        not null,
    knowledge_id bigint        not null,
    document_id  varchar(100)        not null,
    position     int           not null,
    content      varchar(1024) not null,
    word_count   int                    default 0,
    keywords     text,
    index idx_tenant_id_knowledge_id_document_id (tenant_id, knowledge_id, document_id)
) default charset utf8mb4;
