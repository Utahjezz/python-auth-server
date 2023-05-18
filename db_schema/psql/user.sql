create extension if not exists "uuid-ossp";

create table users (
    id uuid not null default uuid_generate_v4(),
    email varchar(254) not null,
    password varchar(255) not null,
    first_name varchar(255) not null,
    last_name varchar(255) not null,
    two_factor_enabled boolean not null default false,

    constraint user_pkey primary key (id),
    constraint user_email_key unique (email)
);
create index user_email_idx on users (email);
