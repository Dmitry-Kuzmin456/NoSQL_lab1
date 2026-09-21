#!/bin/bash
# Sourced by basho riak-cluster.sh after riak_kv is up. Do not `exit`.

$RIAK_ADMIN bucket-type create kv '{"props":{"allow_mult":true,"dvv_enabled":true}}' || true
$RIAK_ADMIN bucket-type activate kv || true
