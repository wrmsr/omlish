#!/bin/sh
set -eu

INTERNAL_UID=$(id -u "$SHIFTUID_INTERNAL_USER")

if [ "$SHIFTUID_EXTERNAL_UID" != "$INTERNAL_UID" ]; then
  # 1. Evict any existing user squatting on our target UID
  CONFLICT_USER=$(getent passwd "$SHIFTUID_EXTERNAL_UID" | cut -d: -f1)
  if [ -n "$CONFLICT_USER" ] && [ "$CONFLICT_USER" != "$SHIFTUID_INTERNAL_USER" ]; then
      userdel "$CONFLICT_USER"
  fi

  # 2. Ensure the target group exists
  getent group "$SHIFTUID_EXTERNAL_GID" >/dev/null 2>&1 || groupadd -g "$SHIFTUID_EXTERNAL_GID" shift-uid

  # 3. Temporarily point home dir away to bypass the automatic large chown
  INTERNAL_HOME=$(getent passwd "$SHIFTUID_INTERNAL_USER" | cut -d: -f6)
  usermod -d /tmp "$SHIFTUID_INTERNAL_USER"

  # 4. Shift user's primary UID and GID to match the host, keeping original group
  usermod -u "$SHIFTUID_EXTERNAL_UID" -g "$SHIFTUID_EXTERNAL_GID" -aG "$INTERNAL_UID" "$SHIFTUID_INTERNAL_USER"

  # 5. Point the home directory back
  usermod -d "$INTERNAL_HOME" "$SHIFTUID_INTERNAL_USER"
fi

_INTERNAL_USER="$SHIFTUID_INTERNAL_USER"
_INTERNAL_ENTRYPOINT="$SHIFTUID_INTERNAL_ENTRYPOINT"

unset SHIFTUID_EXTERNAL_UID
unset SHIFTUID_EXTERNAL_GID
unset SHIFTUID_INTERNAL_USER
unset SHIFTUID_INTERNAL_ENTRYPOINT

exec gosu "$_INTERNAL_USER" $_INTERNAL_ENTRYPOINT $@
