create table tenant (
    id         bigint       not null auto_increment primary key,
    created_at timestamp    not null default current_timestamp,
    updated_at timestamp    not null default current_timestamp on update current_timestamp,
    deleted    tinyint      not null default 0,
    name       varchar(100) not null,
    email_domain     varchar(100) not null,
    is_active  tinyint      not null default 1,
    is_setup   tinyint      not null default 0,
    unique key uk_name (name),
    unique key uk_email_domain (email_domain)
) default charset utf8mb4;


create table user (
    id              bigint       not null auto_increment primary key,
    created_at      timestamp    not null default current_timestamp,
    updated_at      timestamp    not null default current_timestamp on update current_timestamp,
    deleted         tinyint      not null default 0,
    tenant_id       bigint       not null,
    name            varchar(255) not null,
    email           varchar(255) not null,
    full_name       varchar(255) null     default null,
    avatar          varchar(255) null     default null,
    hashed_password varchar(100) not null,
    role            varchar(100) not null,
    status          varchar(50)  not null,
    unique key uk_tenant_id_name (tenant_id, name),
    unique key uk_email (email)
) default charset utf8mb4;

insert into tenant(name, email_domain)
values ('dreamcat', 'dreamcat.org');
