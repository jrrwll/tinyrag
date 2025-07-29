
insert into tenant(name, email_domain)
values ('dreamcat', 'dreamcat.org');

insert into user(tenant_id, email, role, status, hashed_password)
values (1, 'tinyrag@dreamcat.org', 'owner', 'active',
        '$2b$12$OnCny4KDBuZf7uzSAUI0au.HpOQoyhnnx8QudJxvfuSLUvL4kQOGu');
