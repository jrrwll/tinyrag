create table workspace (
    id                     bigint        not null auto_increment primary key,
    created_at             timestamp     not null default current_timestamp,
    updated_at             timestamp     not null default current_timestamp on update current_timestamp,
    deleted                tinyint       not null default 0,
    tenant_id              bigint        not null,
    name                   varchar(100)  not null,
    description            varchar(1000) null     default null,
    llm_model_config       longtext,
    embedding_model_config longtext,
    vector_store_config    longtext
) default charset utf8mb4;


create table model (
    id            bigint       not null auto_increment primary key,
    created_at    timestamp    not null default current_timestamp,
    updated_at    timestamp    not null default current_timestamp on update current_timestamp,
    deleted       tinyint      not null default 0,
    tenant_id     bigint       not null,
    provider_name varchar(255) not null,
    model_name    varchar(255) not null,
    type          varchar(50)  not null,
    enable        tinyint      not null default 1,
    config        longtext
) default charset utf8mb4;


create table tenant_default_model (
    id         bigint       not null auto_increment primary key,
    created_at timestamp    not null default current_timestamp,
    updated_at timestamp    not null default current_timestamp on update current_timestamp,
    deleted    tinyint      not null default 0,
    tenant_id  bigint       not null,
    model_type varchar(50)  not null,
    model_id   bigint       null     default null,
    model_name varchar(255) null     default null,
    unique key uk_tenant_id_model_type (tenant_id, model_type)
) default charset utf8mb4;


create table vector_store (
    id         bigint      not null primary key,
    created_at timestamp   not null default current_timestamp,
    updated_at timestamp   not null default current_timestamp on update current_timestamp,
    deleted    tinyint     not null default 0,
    tenant_id  bigint      not null,
    type       varchar(50) not null,
    enable     tinyint     not null default 1,
    config     longtext
) default charset utf8mb4;


create table async_task (
    id           bigint       not null primary key,
    created_at   timestamp    not null default current_timestamp,
    tenant_id    bigint       not null,
    workspace_id bigint       not null,
    type         varchar(50)  not null,
    ref_id       varchar(100) null     default null,
    payload      longtext,
    status       varchar(50)  not null,
    submitted_at timestamp    not null default current_timestamp,
    started_at   timestamp    null     default null,
    completed_at timestamp    null     default null,
    result       longtext              default null,
    progress     int                   default 0
) default charset utf8mb4;
