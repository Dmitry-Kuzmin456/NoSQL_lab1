#!/bin/bash
# Sourced by basho riak-cluster.sh after riak_kv is up. Do not `exit`.

create_and_activate() {
  local type_name=$1
  local props=$2

  $RIAK_ADMIN bucket-type create "$type_name" "$props" 2>/dev/null || true
  for _ in $(seq 1 10); do
    if $RIAK_ADMIN bucket-type activate "$type_name" 2>/dev/null; then
      break
    fi
    sleep 1
  done
}

# CRDT datatypes
create_and_activate "counters" '{"props":{"datatype":"counter","allow_mult":true}}'
create_and_activate "sets"     '{"props":{"datatype":"set","allow_mult":true}}'
create_and_activate "maps"     '{"props":{"datatype":"map","allow_mult":true}}'

# Key-Value with siblings & DVV
create_and_activate "kv"       '{"props":{"allow_mult":true,"dvv_enabled":true}}'

touch /tmp/.riak_initialized
