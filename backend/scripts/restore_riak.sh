#!/usr/bin/env bash
set -e

BACKUP="${1:-riak_backup.tar.gz}"
CONTAINER="${2:-nosql_riak_test}"

if [ ! -f "$BACKUP" ]; then
    echo "Ошибка: файл '$BACKUP' не найден."
    exit 1
fi

echo "Восстановление данных Riak в контейнер '$CONTAINER' из '$BACKUP'..."
docker exec "$CONTAINER" riak stop >/dev/null 2>&1 || true
cat "$BACKUP" | docker exec -i "$CONTAINER" tar -xzf - -C /var/lib/
docker exec "$CONTAINER" chown -R riak:riak /var/lib/riak
docker exec "$CONTAINER" riak start
docker exec "$CONTAINER" riak-admin wait-for-service riak_kv
echo "Восстановление успешно завершено!"
