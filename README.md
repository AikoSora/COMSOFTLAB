# COMSOFTLAB
A test assignment for a Python developer vacancy at COMSOFTLAB

## Run with docker-compose

Copy and rename `.env.dist` file
```zsh
cp .env.dist .env
```

Run application
```zsh
docker-compose up -d
```

Perform the migration
```zsh
docker-compose exec -w /app django python manage.py migrate
```

Create superuser in admin
```zsh
docker-compose exec -w /app django python manage.py createsuperuser
```

Access to the site will be available via the link: `http://localhost:1081/`
