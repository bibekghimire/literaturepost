# Getting Started
## clone the repo
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
## Install Dependencies
```bash
pip install -r requirements.txt
```
## Set up environment variables
```bash

ENGINE -> database Engine: django.db.backends.postgresql
DB_NAME : Database Name
DB_USER: User account
DB_PASSWORD: password for database user
DB_HOST: host address database is running
DB_PORT: port at which database is listening
SECRET_KEY: Secret Key 
```
## Run migrations
```bash
python manage.py migrate
```
## Run the development server
```bash
python manage.py runserver
```
## Running Test
python manage.py test
