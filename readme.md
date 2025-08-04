# literature post

This project `literaturepost' is a Django-based web application for publishing Literature posts. CRUD for Poem, Gajal, Story. 

For User management only the register user with privileges can create other users.
## Getting Started
### clone the repo
```bash
git clone https://github.com/bibekghimire/literaturepost.git
cd literaturepost
```

## Create and Activate Virtual Environment
```bash
python -m venv venv
#windows
venv\Scripts\activate
#Linux/macOS
source venv/bin/activate
```
### Install Dependencies
```bash
pip install -r requirements.txt
```
### Set up environment variables
```bash

ENGINE -> database Engine: django.db.backends.postgresql
DB_NAME : Database Name
DB_USER: User account
DB_PASSWORD: password for database user
DB_HOST: host address database is running
DB_PORT: port at which database is listening
SECRET_KEY
```
### Run migrations
```bash
python manage.py migrate
```
### Run the development server
```bash
python manage.py runserver
```


## Running Test
python manage.py test

## API Endpoints
### Authentication Endpoints (JWT-based)
- `POST /api/login/` — Get access & refresh tokens  
- `POST /api/token/refresh/` — Refresh access token  
- `POST /api/token/verify/` — Verify token validity
- `POST /api/logout/` - Logout 


## features
- REST API with django_rest_framework
- User registration (from authentecateduser only)
- Customized User Roles
- Customized User Dashboard Support
- CRUD operations for Poem, Gajal, Story

## tech stack
- **Backend:** Django, Django REST Framework
- **Database:** PostgreSQL/SqLite

