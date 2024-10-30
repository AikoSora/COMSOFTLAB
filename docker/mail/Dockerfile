FROM python:3.13

RUN mkdir /app

WORKDIR /app

COPY Pipfile Pipfile.lock .

RUN pip install pipenv

RUN pipenv install --dev --system --deploy

COPY app .

RUN python manage.py collectstatic --noinput

CMD daphne -b 0.0.0.0 -p 8000 src.asgi:application