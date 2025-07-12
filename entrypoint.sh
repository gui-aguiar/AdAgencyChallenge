#!/bin/bash

echo "waiting RabbitMQ..."

until nc -z rabbitmq 5672; do
  sleep 1
done

echo "RabbitMQ is ready. Running migrations..."
python manage.py migrate
echo "Starting server..."

exec "$@"
