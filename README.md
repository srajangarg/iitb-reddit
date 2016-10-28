# iitb-reddit

### Python version 2.7
```
sudo apt install python=2.7
```

### Django version 1.9
```
sudo apt install python-pip
sudo pip install django==1.9
```

### Postgresql version 9.5
```
sudo apt install postgresql=9.5
sudo apt install postgresql-server-dev-9.5
sudo service postgresql start
```

### Other requirements
```
sudo pip install psycopg2==2.6
```

### Setting up Postgres Database
```
sudo su - postgres
psql
create user admin with password 'admin';
create database reddit owner admin;
\q
logout
python manage.py test # to test if setup working
```

### Database access
```
psql admin -h localhost -d reddit
# password admin
```