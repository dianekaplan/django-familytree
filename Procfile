# web: gunicorn --chdir mysite mysite.wsgi
web: daphne --chdir mysite -b 0.0.0.0 -p $PORT mysite.asgi:application
# web: daphne -b 0.0.0.0:$PORT mysite.mysite.asgi:application
