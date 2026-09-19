#!/usr/bin/env bash
set -e

FLAG_FILE="/var/lib/riak/.types_initialized"

if [ -f "$FLAG_FILE" ]; then
    exit 0
fi

ADMIN_ARGS=()
if [ -n "$RIAK_NODE" ]; then
    ADMIN_ARGS+=("-n" "$RIAK_NODE")
fi

echo "Waiting for Riak KV..."
riak-admin "${ADMIN_ARGS[@]}" wait-for-service riak_kv >/dev/null 2>&1 || {
    echo "Riak KV not ready."
    exit 1
}

echo "Initializing Riak bucket types..."

create_and_activate_type() {
    local TYPE_NAME=$1
    local PROPS=$2

    riak-admin "${ADMIN_ARGS[@]}" bucket-type create "$TYPE_NAME" "$PROPS" 2>/dev/null || true
    riak-admin "${ADMIN_ARGS[@]}" bucket-type activate "$TYPE_NAME" 2>/dev/null || true
}

# CRDT
create_and_activate_type "counters" '{"props":{"datatype":"counter","allow_mult":true}}'
create_and_activate_type "sets" '{"props":{"datatype":"set","allow_mult":true}}'
create_and_activate_type "maps" '{"props":{"datatype":"map","allow_mult":true}}'

# KV
create_and_activate_type "kv" '{"props":{"allow_mult":true,"dvv_enabled":true}}'

touch "$FLAG_FILE" 2>/dev/null || true
echo "Riak bucket types initialized."
