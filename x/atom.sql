/*
TODO:
* fault table - arbitrary columns, indices
* activity table
*/

create type atom_state as enum (
    'committing',
    'committed',
    'compensating',
    'compensated'
);

create sequence atom_id;

create table atom (
    id int unique not null,

    root_id int not null references atom (id) on delete restrict,
    parent_id int references atom (id) on delete restrict,
    prev_sibling_id int references atom (id) on delete restrict,
    active_child_id int references atom (id) on delete restrict,

    primary key (root_id, id),

    time_created timestamp not null default now(),
    user_created name not null default current_user,
    time_updated timestamp not null default now(),
    user_updated name not null default current_user,

    ttl_absolute interval,
    deadline_absolute timestamp,
    ttl_relative interval,
    deadline_relative timestamp,

    is_faulted boolean not null default false,
    fault_info text,

    state atom_state not null default 'committing',
    compensation_attempts int not null default 0,

    input text,
    context text,
    output text,

    constraint self_root_no_parent_check check ((id = root_id) = (parent_id is null)),
    constraint no_self_parent_check check (parent_id != id),
    constraint no_output_without_input_check check (not (output is not null and input is null)),
    constraint no_children_with_input_check check
        (not (active_child_id is not null and input is not null)),

    constraint no_absolute_deadline_if_not_committing_check check
        (not (deadline_absolute is not null and state != 'committing')),
    constraint no_relative_deadline_if_not_committing_check check
        (not (deadline_relative is not null and state != 'committing'))
);

create type atom_log_action as enum (
    'insert',
    'update'
);

create sequence atom_log_id;

create table atom_log (
    log_id int unique,
    log_action atom_log_action not null,

    like atom,

    primary key (root_id, log_id),

    constraint root_id_fk foreign key (root_id) references atom (id) match full on delete cascade
);

create function before_atom_log_update() returns trigger as $$
begin

    raise exception 'Log updates not allowed';

end; $$ language 'plpgsql';

create trigger before_atom_log_update_trigger before update on atom_log
    for each row execute procedure before_atom_log_update();

create index atom_absolute_deadline_index on atom (deadline_absolute)
    where deadline_absolute is not null and is_faulted = false;

create index atom_relative_deadline_index on atom (deadline_relative)
    where deadline_relative is not null and is_faulted = false;

create index atom_faulted_index on atom (is_faulted) where is_faulted = true;

create function before_atom_insert() returns trigger as $$
declare
    v_parent atom;
    v_parent_active_child atom;
begin

    -- Simple immutables

    if new.id is not null then
        raise exception 'Cannot insert id %', new.id;
    end if;

    if new.root_id is not null then
        raise exception 'Cannot insert root_id %', new.id;
    end if;

    if new.prev_sibling_id is not null then
        raise exception 'Cannot insert prev_sibling_id %', new.prev_sibling_id;
    end if;

    if new.active_child_id is not null then
        raise exception 'Cannot insert active_child_id %', new.active_child_id;
    end if;

    if new.time_created != now() then
        raise exception 'Cannot insert time_created %', new.time_created;
    end if;

    if new.user_created != current_user then
        raise exception 'Cannot insert user_created %', new.user_created;
    end if;

    if new.time_updated != now() then
        raise exception 'Cannot insert time_updated %', new.time_updated;
    end if;

    if new.user_updated != current_user then
        raise exception 'Cannot insert user_updated %', new.user_updated;
    end if;

    if new.deadline_absolute is not null then
        raise exception 'Cannot insert deadline_absolute %', new.deadline_absolute;
    end if;

    if new.deadline_relative is not null then
        raise exception 'Cannot insert deadline_relative %', new.deadline_relative;
    end if;

    if new.state != 'committing' then
       raise exception 'Cannot insert state %', new.state;
    end if;

    if new.compensation_attempts != 0 then
       raise exception 'Cannot insert compensation_attempts %', new.compensation_attempts;
    end if;

    -- ID

    select into new.id nextval('atom_id');

    -- Pre-linkage

    if new.parent_id is not null then
        select into v_parent * from atom where id = new.parent_id;
        if not found then
            raise exception 'Parent atom not found', new.parent_id;
        end if;

        if v_parent.state != 'committing' then
            raise exception 'Parent atom % not committing', v_parent.state;
        end if;

        if v_parent.is_faulted then
            raise exception 'Parent atom is faulted';
        end if;

        if v_parent.active_child_id is not null then
            select into v_parent_active_child * from atom where id = v_parent.active_child_id;
            if not found then
                raise exception 'Parent active child atom not found', v_parent.active_child_id;
            end if;

            if v_parent_active_child.state != 'committed' then
                raise exception 'Parent active child % not committed', v_parent_active_child.state;
            end if;
        end if;

        new.root_id = v_parent.root_id;
        new.prev_sibling_id = v_parent.active_child_id;

    else
        new.root_id := new.id;

    end if;

    return new;

end; $$ language 'plpgsql';

create trigger before_atom_insert_trigger before insert on atom
    for each row execute procedure before_atom_insert();

create function after_atom_insert() returns trigger as $$
declare
    v_parent atom;
    v_parent_active_child atom;
begin

    -- Post-linkage

    -- Even though we have an ID in the before trigger the ref constrait would explode.
    if new.parent_id is not null then
        update atom set active_child_id = new.id
            where id = new.parent_id and
                (active_child_id = new.prev_sibling_id or
                    (active_child_id is null and new.prev_sibling_id is null));
        if not found then
            raise exception 'Failed to link atom to parent';
        end if;
    end if;

    insert into atom_log select nextval('atom_log_id'), 'insert', new.*;

    return new;

end; $$ language 'plpgsql';

create trigger after_atom_insert_trigger after insert on atom
    for each row execute procedure after_atom_insert();

create function before_atom_update() returns trigger as $$
begin

    -- Simple immutables

    if old.id != new.id then
        raise exception 'Cannot update id (from % to %)', old.id, new.id;
    end if;

    if old.root_id != new.root_id then
        raise exception 'Cannot update root_id (from % to %)', old.root_id, new.root_id;
    end if;

    if old.parent_id != new.parent_id then
        raise exception 'Cannot update parent_id (from % to %)', old.parent_id, new.parent_id;
    end if;

    if old.prev_sibling_id != new.prev_sibling_id then
        raise exception 'Cannot update prev_sibling_id (from % to %)',
            old.prev_sibling_id, new.prev_sibling_id;
    end if;

    if old.time_created != new.time_created then
        raise exception
            'Cannot update time_created (from % to %)', old.time_created, new.time_created;
    end if;

    if old.user_created != new.user_created then
        raise exception
            'Cannot update user_created (from % to %)', old.user_created, new.user_created;
    end if;

    if old.time_updated != new.time_updated then
        raise exception
            'Cannot update time_updated (from % to %)', old.time_updated, new.time_updated;
    end if;

    if old.user_updated != new.user_updated then
        raise exception
            'Cannot update user_updated (from % to %)', old.user_updated, new.user_updated;
    end if;

    if old.deadline_absolute != new.deadline_absolute then
        raise exception
            'Cannot update deadline_absolute (from % to %)',
            old.deadline_absolute, new.deadline_absolute;
    end if;

    if old.deadline_relative != new.deadline_relative then
        raise exception
            'Cannot update deadline_relative (from % to %)',
            old.deadline_relative, new.deadline_relative;
    end if;

    if old.input != new.input then
        raise exception 'Cannot update input (from % to %)', old.input, new.input;
    end if;

    -- Times and users

    new.time_updated := now();
    new.user_updated := current_user;

    if new.state = 'committing' then
        -- Invalid state of (non-committing + deadline) checked in table constraint

        if new.ttl_absolute is not null then
            new.deadline_absolute := now() + new.ttl_absolute;
        end if;

        if new.ttl_relative is not null then
            new.deadline_relative := now() + new.ttl_relative;
        end if;

    else
        new.deadline_absolute := null;
        new.deadline_relative := null;

    end if;

    -- Faults

    if old.is_faulted != new.is_faulted and old.parent_id is not null then
        -- Recursive
        update atom set is_faulted = new.is_faulted where id = old.parent_id;
    end if;

    -- Context

    -- Note this checks old.state, so update set context = xyz, state = 'committed' is legal.
    if old.context != new.context then
        if old.state != 'committing' then
            raise exception 'Cannot update context on non-committing';
        end if;

        if new.is_faulted then
            raise exception 'Cannot set context while faulted';
        end if;
    end if;

    -- State transitions

    -- Complex checks should be done in here - the state of the world is assumed safe, so only guard
    -- in transitions. This is very important to bear in mind - 'fault' must always be able to
    -- propegate through.

    if old.state != new.state then

        -- Simple checks

        if new.state = 'committing' then
            raise exception 'Cannot update state to committing';

        elseif new.state = 'committed' then
            if old.state != 'committing' then
                raise exception 'Cannot update state to committing from %', old.state;
            end if;

        elseif new.state = 'compensating' then
            if old.state not in ('committing', 'committed') then
                raise exception 'Cannot update state to compensating from %', old.state;
            end if;

        elseif new.state = 'compensated' then
            if old.state != 'compensating' then
                raise exception 'Cannot update state to compensated from %', old.state;
            end if;

        else
            -- Here to guard against extending the enum and forgetting to update the trigger
            raise exception 'Unhandled state %', new.state;

        end if;
    end if;

    -- Parent checks

    -- todo

    -- Child checks

    if new.active_child_id is not null then
        raise exception 'Cannot update compensated with active child %', new.active_child_id;
    end if;

    update atom set active_child_id = new.prev_sibling_id where id = new.parent_id;
    if not found then
        raise exception 'Failed to update parent';
    end if;

    return new;

end; $$ language 'plpgsql';

create trigger before_atom_update_trigger before update on atom
    for each row execute procedure before_atom_update();

create function after_atom_update() returns trigger as $$
declare
    v_active_child atom;
begin

    -- Linkage

    -- if new.active_child_id is not null then
    --    select into v_active_child * from atom where id = new.active_child_id;
    --    if not found then
    --        raise exception 'Active child % not found', new.active_child_id;
    --    end if;

    --    if new.state = 'committing' then
    --        if v_active_child.state not in ('committing', 'committed') then
    --            raise exception
    --                'Illegal active child state % with parent state %',
    --                v_active_child.state, new.state;
    --        end if;

    --    elseif new.state = 'committed' then
    --        if v_active_child.state != 'committed' then
    --            raise exception
    --                'Illegal active child state % with parent state %',
    --                v_active_child.state, new.state;
    --        end if;

    --    elseif new.state = 'compensating' then
    --        if v_active_child.state != 'compensating' then
    --            raise exception
    --                'Illegal active child state % with parent state %',
    --                v_active_child.state, new.state;
    --        end if;

    --    elseif new.state = 'compensated' then
    --        raise exception
    --            'Illegal active child with parent state %', v_active_child.state;

    --    else
    --        -- Here to guard against extending the enum and forgetting to update the trigger
    --        raise exception 'Unhandled state %', new.state;

    --    end if;
    -- end if;

    insert into atom_log select nextval('atom_log_id'), 'update', new.*;

    -- if new.state = 'committed' and new.id = new.root_id then
    --    delete from atom where id = new.id;
    -- end if;

    return new;

end; $$ language 'plpgsql';

create trigger after_atom_update_trigger after update on atom
    for each row execute procedure after_atom_update();

create function before_atom_delete() returns trigger as $$
declare
    v_tmp_atom atom;
begin

    if old.state not in ('committed', 'compensated') then
        raise exception 'Cannot delete atom of state %', old.state;
    end if;

end; $$ language 'plpgsql';

create trigger before_atom_delete_trigger before delete on atom
    for each row execute procedure before_atom_delete();

/*
begin(parent, input)
abort(id)
fault(id, info)
commit(id, output)

touch(id)

get_context(id)
set_context(id, context)

crossbar involves async callbacks anyway. like locks, it will be built with this, but isn't thins.

ignore acquisition, ignore immediate rollback
*/
