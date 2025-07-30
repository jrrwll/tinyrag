create table tenant (
    id           bigint       not null auto_increment primary key,
    created_at   timestamp    not null default current_timestamp,
    updated_at   timestamp    not null default current_timestamp on update current_timestamp,
    name         varchar(100) not null,
    email_domain varchar(100) not null,
    is_active    tinyint      not null default 1,
    is_setup     tinyint      not null default 0,
    unique key uk_name (name),
    unique key uk_email_domain (email_domain)
) default charset utf8mb4;


create table user (
    id              bigint       not null auto_increment primary key,
    created_at      timestamp    not null default current_timestamp,
    updated_at      timestamp    not null default current_timestamp on update current_timestamp,
    tenant_id       bigint       not null,
    email           varchar(255) not null,
    name            varchar(255)
        generated always as (substring_index(email, '@', 1)) stored,
    full_name       varchar(255) null     default null,
    avatar          varchar(255) null     default null,
    hashed_password varchar(100) not null,
    role            varchar(100) not null,
    status          varchar(50)  not null,
    unique key uk_tenant_id_name (tenant_id, name),
    unique key uk_email (email)
) default charset utf8mb4;


create table permission (
    id            bigint       not null auto_increment primary key,
    created_at    timestamp    not null default current_timestamp,
    updated_at    timestamp    not null default current_timestamp on update current_timestamp,
    tenant_id     bigint       not null,
    resource_type varchar(100) not null,
    resource_id   bigint       not null,
    user_identify varchar(255) not null,
    role          varchar(100) not null,
    unique key uk_resource_user_identify (tenant_id, resource_type, resource_id, user_identify),
    key idx_resource_type_user_identify(tenant_id, resource_type, user_identify),
    key idx_resource_type_updated_at(tenant_id, resource_type, updated_at)
) default charset utf8mb4;
