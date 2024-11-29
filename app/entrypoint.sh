#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -o errexit
# Exit if any of the intermediate steps in a pipeline fails.
set -o pipefail
# Exit if trying to use an uninitialized variable.
set -o nounset

CONTAINER_NAME=${CONTAINER_NAME:-"none"}

# if [ "$CONTAINER_NAME" == "web" ]; then
#     python manage.py makemigrations
#     python manage.py migrate
#     python manage.py create_default_django_superuser
#     python manage.py create_default_user
#     python manage.py create_default_admin
#     python manage.py collectstatic --no-input --clear
# fi

python manage.py makemigrations
python manage.py migrate
python manage.py create_default_django_superuser
python manage.py create_default_user
python manage.py create_default_admin
python manage.py collectstatic --no-input --clear

exec "$@"