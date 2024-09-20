create role secrets_owner_role;
grant connect on database omlish to secrets_owner_role;
create user secrets_owner with password 'secrets_owner_password';
grant secrets_owner_role to secrets_owner;

create schema secrets authorization secrets_owner_role;

create table secrets.secrets (
  key varchar primary key not null,
  value varchar not null,
  created_at timestamp not null default now()
);
alter table secrets.secrets owner to secrets_owner_role;

create table secrets.secrets_accesses (
  key varchar primary key not null,
  access_user varchar not null,
  inet_client_addr varchar not null,
  accessed_at timestamp not null default now()
);
alter table secrets.secrets_accesses owner to secrets_owner_role;

create or replace function secrets.access_secret(
  key varchar
) returns varchar as $$
#variable_conflict use_variable
begin
  insert into secrets.secrets_accesses
    (key, access_user, inet_client_addr)
  values
    (key, current_user, inet_client_addr());
  return (select value from secrets.secrets where key = key);
end
$$
  language plpgsql
  security definer
  set search_path = secrets;
alter function secrets.access_secret owner to secrets_owner_role;

--

create role secrets_reader_role;
grant connect on database omlish to secrets_reader_role;
create user secrets_reader with password 'secrets_reader_password';
grant secrets_reader_role to secrets_reader;

grant usage on schema secrets to secrets_reader_role;
grant execute on function secrets.access_secret(varchar) to secrets_reader_role;
