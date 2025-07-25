create user tinyrag with password 'tinyrag';

create database tinyrag_vector;

alter database tinyrag_vector owner to tinyrag;

grant all privileges on database tinyrag_vector to tinyrag;

# \c tinyrag_vector
# create extension if not exists vector
