create table workflow (
    id          bigint       not null auto_increment primary key,
    created_at  timestamp    not null default current_timestamp,
    updated_at  timestamp    not null default current_timestamp on update current_timestamp,
    deleted     tinyint      not null default 0,
    name        varchar(100) not null,
    description varchar(1000)         default null,
    type        varchar(32)  not null
);

create table node (
    id          varchar(36)  not null primary key,
    deleted     tinyint      not null default 0,
    workflow_id bigint       not null,
    type        varchar(32)  not null,
    name        varchar(100) not null,
    description varchar(1000)         default null,
    model_id    bigint                default null,
    front_info  longtext
);

create table edge (
    id          varchar(36) not null primary key,
    deleted     tinyint     not null default 0,
    workflow_id bigint      not null,
    source      varchar(36) not null,
    target      varchar(36) not null,
    predicate   text,
    front_info  longtext
);
