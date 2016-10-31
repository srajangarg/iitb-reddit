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
./manage.py test # to test if setup working
```

### Database access
```
./manage.py dbshell
```

### Running Django
```
./manage.py makemigrations
./manage.py migrate
./manage.py runserver
```

### Django admin
```
# available on /admin

echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@admin.com', 'admin')" | python manage.py shell
```

### To view SQL generated by Django
```
./manage.py sqlmigrate `appname` `migration #`
```

eg.

```
./manage.py sqlmigrate users 0001
```

### Messed stuff up?
```
for F in `echo "\dt" | ./manage.py dbshell | awk -F ' ' '{print $3}' | awk 'NR > 3'`; do echo "drop table $F cascade;" | ./manage.py dbshell; done

find . -type f | grep "migrations" | grep -v "__init__" | xargs rm -rf

echo "from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser('admin', 'admin')" | python manage.py shell
```
