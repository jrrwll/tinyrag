
create table workflow (
    id          bigint     not null auto_increment primary key,
    created_at  timestamp    not null default current_timestamp,
    updated_at  timestamp    not null default current_timestamp on update current_timestamp,
    deleted     tinyint      not null default 0,
    name        varchar(100) not null,
    description varchar(1000)         default null,
    status      varchar(50)  not null,
    graph       longtext
) default charset utf8mb4;

create table workflow_run (
    id          bigint  not null primary key,
    created_at  timestamp not null default current_timestamp,
    updated_at  timestamp not null default current_timestamp on update current_timestamp,
    deleted     tinyint   not null default 0,
    workflow_id bigint  not null,
    started_at  timestamp null     default null,
    stopped_at  timestamp null     default null
) default charset utf8mb4;
