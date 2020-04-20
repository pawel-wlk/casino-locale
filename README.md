# About project
Online card games app.

# Development manual

## Install pipenv
```
pip install pipenv
```

## Install dependencies
```
pipenv install
```

## Useful commands
Run server
```
pipenv run python manage.py runserver
```
Make migrations
```
pipenv run python manage.py makemigrations
```
Migrate
```
pipenv run python manage.py migrate
```

Alternatively, you can run `pipenv shell` to enter virtual env shell so you can run above commands without `pipenv run` part.
In order to exit this shell type `exit`.
