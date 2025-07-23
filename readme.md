# literature post

This project `literaturepost' is a Django-based web application for publishing Literature posts. CRUD for Poem, Gajal, Story. 

For User management only the register user with privileges can create other users. 

## features
- REST API with django_rest_framework
- User registration (from authnticated user only)
- Customized User Roles
- Customized User Dashboard Support
- CRUD operations for Poem, Gajal, Stroy

## tech stack
- **Backend:** Django, Django REST Framework
- **Database:** PostgreSQL/SqLite

## Getting Started
### clone the repo
```bash
git clone https://github.com/bibekghimire/literaturepost.git
cd literaturepost
```
### create and activate virtual environment
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
ENGINE=django.db.backends.postgresql
DB_NAME= your_db_name
DB_USER=your_db_user
DB_PASSWORD=db_password
DB_HOST=Your_host
DB_PORT=your_port
```
### Run migrations
```bash
python manage.py migrate
```
### Run the development server
```bash
python manage.py runserver
```
