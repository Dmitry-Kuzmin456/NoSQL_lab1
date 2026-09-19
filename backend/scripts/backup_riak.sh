#!/usr/bin/env bash
set -e

CONTAINER="${1:-nosql_riak_test}"
OUTPUT="${2:-riak_backup.tar.gz}"

echo "Сохранение данных Riak из контейнера '$CONTAINER' в '$OUTPUT'..."
docker exec "$CONTAINER" tar -czf - -C /var/lib riak > "$OUTPUT"
echo "Готово: $OUTPUT ($(du -h "$OUTPUT" | cut -f1))"
