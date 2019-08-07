# Protecton backend

Run tests and flake8:

    docker-compose run --rm app sh -c "python manage.py test && flake8"

Create superuser

    docker-compose run --rm app sh -c "python manage.py createsuperuser"