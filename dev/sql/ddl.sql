create table model (
    id            bigint       not null auto_increment primary key,
    created_at    timestamp    not null default current_timestamp,
    updated_at    timestamp    not null default current_timestamp on update current_timestamp,
    deleted       tinyint      not null default 0,
    provider_name varchar(100) not null,
    model_name    varchar(100) not null,
    type          varchar(32)  not null,
    enable        tinyint      not null default 1,
    config        longtext,
    embedding_config longtext
) default charset utf8mb4;

create table default_model (
    id         bigint      not null auto_increment primary key,
    created_at timestamp   not null default current_timestamp,
    updated_at timestamp   not null default current_timestamp on update current_timestamp,
    deleted    tinyint     not null default 0,
    model_type varchar(32) not null,
    model_id   bigint               default null,
    unique key uk_model_type (model_type)
) default charset utf8mb4;

create table workflow (
    id          bigint       not null auto_increment primary key,
    created_at  timestamp    not null default current_timestamp,
    updated_at  timestamp    not null default current_timestamp on update current_timestamp,
    deleted     tinyint      not null default 0,
    name        varchar(100) not null,
    description varchar(1000)         default null,
    status      varchar(32)  not null,
    graph       longtext
) default charset utf8mb4;

create table workflow_run (
    id          bigint    not null auto_increment primary key,
    created_at  timestamp not null default current_timestamp,
    updated_at  timestamp not null default current_timestamp on update current_timestamp,
    deleted     tinyint   not null default 0,
    workflow_id bigint    not null,
    started_at  timestamp null     default null,
    stopped_at  timestamp null     default null
) default charset utf8mb4;

create table file (
    id         char(32)     not null primary key,
    created_at timestamp    not null default current_timestamp,
    deleted    tinyint      not null default 0,
    type       varchar(32)  not null,
    name       varchar(100) not null,
    size       bigint       not null,
    mime_type  varchar(100) not null
) default charset utf8mb4;

create table dataset (
    id              bigint       not null auto_increment primary key,
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

create table document (
    id          bigint    not null auto_increment primary key,
    created_at  timestamp not null default current_timestamp,
    updated_at  timestamp not null default current_timestamp on update current_timestamp,
    deleted     tinyint   not null default 0,
    dataset_id  bigint    not null,
    position    int       not null,
    word_count  int                default 0,
    source_type varchar(32),
    source_info text,
    indexing    tinyint   not null default 0
) default charset utf8mb4;

create table document_chunk (
    id           bigint        not null auto_increment primary key,
    created_at   timestamp     not null default current_timestamp,
    updated_at   timestamp     not null default current_timestamp on update current_timestamp,
    deleted      tinyint       not null default 0,
    dataset_id   bigint        not null,
    document_id  bigint        not null,
    position     int           not null,
    content      varchar(1024) not null,
    word_count   int                    default 0,
    keywords     text,
    index_doc_id varchar(100)  null     default null
) default charset utf8mb4;

create table async_task (
    id           char(36)     not null primary key,
    created_at   timestamp    not null default current_timestamp,
    updated_at   timestamp    not null default current_timestamp on update current_timestamp,
    name         varchar(100) not null,
    payload      longtext     not null,
    status       varchar(32)  not null,
    submitted_at timestamp    not null default current_timestamp,
    started_at   timestamp    null     default null,
    completed_at timestamp    null     default null,
    result       longtext              default null,
    progress     int                   default 0
) default charset utf8mb4;
