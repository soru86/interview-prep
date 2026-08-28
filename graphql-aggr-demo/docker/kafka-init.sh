#!/bin/bash
set -e

KAFKA_BIN="${KAFKA_BIN:-/opt/kafka/bin}"
BOOTSTRAP="${KAFKA_BOOTSTRAP:-kafka:29092}"

TOPICS=(
  user.registered
  user.logged_in
  user.logged_out
  order.created
)

for TOPIC in "${TOPICS[@]}"; do
  echo "Creating topic: ${TOPIC}"
  "${KAFKA_BIN}/kafka-topics.sh" \
    --bootstrap-server "${BOOTSTRAP}" \
    --create \
    --if-not-exists \
    --topic "${TOPIC}" \
    --partitions 3 \
    --replication-factor 1
done

echo "Topics:"
"${KAFKA_BIN}/kafka-topics.sh" --bootstrap-server "${BOOTSTRAP}" --list
