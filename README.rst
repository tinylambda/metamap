Use docker to initialize a local test environment
====

Prepare MySQL
----
.. code-block:: shell

 docker run -e MYSQL_ROOT_PASSWORD=mysqlpass -p 3306:3306 -d mysql:5.7
 mysql -uroot -pmysqlpass -h127.0.0.1
 mysql> create database metamap;
 mysql> create user 'game'@'%' identified by 'mysqlpass'
 mysql> grant all privileges on metamap.* to 'game'@'%';

Prepare Redis and Etcd
----
.. code-block:: shell

 docker run -p6379:6379 -d redis
 docker run -d --name Etcd-server --publissh 2379:2379 --publish 2380:2380 --env ALLOW_NONE_AUTHENTICATION=yes --env ETCD_ADVERTISE_CLIENT_URLS=http://localhost:2379 bitnami/etcd:latest

Write a local setting
----
.. code-block:: shell

 vim metamap/settings/local.py

and input the following content:

.. code-block:: python

    from .dev import *

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'metamap',
            'HOST': '127.0.0.1',
            'PORT': 3306,
            'USER': 'game',
            'PASSWORD': 'mysqlpass',
            'OPTIONS': {},
        }
    }

Migrate database definition
----
.. code-block:: shell

 DJANGO_RUNTIME_ENV=local python manage.py migrate

Start access server (WebSocket)
----
.. code-block:: shell

 DJANGO_RUNTIME_ENV=local python manage.py runserver

Start a simple WebSocket client
----
.. code-block:: shell

 DJANGO_RUNTIME_ENV=local python core/utils/ws_client.py

Use Let's Encrypt in production environment
====
- https://certbot.eff.org/instructions

Deploy in production environment
====
.. code-block:: python

    # update database configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'metamap',
            'HOST': '127.0.0.1',
            'PORT': 3306,
            'USER': 'game',
            'PASSWORD': 'mysqlpass',
            'OPTIONS': {},
        }
    }
    # disable DEBUG
    DEBUG = False

    # add your domains to ALLOWED_HOSTS
    ALLOWED_HOSTS = ['game-http.domain.com', 'game-ws.domain.com',]

    # allow CSRF on your http server
    CSRF_TRUSTED_ORIGINS = ['https://game-http.domain.com',]