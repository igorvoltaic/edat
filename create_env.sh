echo SECRET_KEY=\'$(openssl rand -hex 32)\' > .env
echo DJANGO_SETTINGS_MODULE=\'base.settings\' >> .env
echo POSTGRES_DB=\'db_$(openssl rand -hex 32| cut -c -8)\' >> .env
echo POSTGRES_USER=\'user_$(openssl rand -hex 32| cut -c -8)\' >> .env 
echo POSTGRES_PASSWORD=\'$(openssl rand -hex 32)\' >> .env
echo POSTGRES_HOST=db >> .env
echo POSTGRES_PORT=5432 >> .env
RABBITMQ_DEFAULT_USER="mquser_$(openssl rand -hex 32| cut -c -8)"
RABBITMQ_DEFAULT_PASS="$(openssl rand -hex 32)"
RABBITMQ_DEFAULT_VHOST=rabbit
echo RABBITMQ_DEFAULT_USER=\'${RABBITMQ_DEFAULT_USER}\' >> .env
echo RABBITMQ_DEFAULT_PASS=\'${RABBITMQ_DEFAULT_PASS}\' >> .env
echo RABBITMQ_DEFAULT_VHOST=\'${RABBITMQ_DEFAULT_VHOST}\' >> .env
echo CELERY_BROKER_URL=\'amqp://${RABBITMQ_DEFAULT_USER}:${RABBITMQ_DEFAULT_PASS}@rabbitmq:5672/${RABBITMQ_DEFAULT_VHOST}\' >> .env

