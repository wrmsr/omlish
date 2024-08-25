drop schema if exists secrets cascade;

drop user if exists secrets_reader;
drop user if exists secrets_owner;

do $$
    declare
        r text;
    begin
        foreach r in array array[
            'secrets_owner_role',
            'secrets_reader_role'
            ] loop
                if exists (select 1 from pg_roles where rolname = r) then
                    execute format('drop owned by %s', r);
                end if;
            end loop;
    end
$$;

drop role if exists secrets_reader_role;
drop role if exists secrets_owner_role;
