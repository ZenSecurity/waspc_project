Getting up and running
----------------------

Basics
^^^^^^

The steps below will get you up and running with a local development environment. We assume you have the following installed:

* pip
* virtualenv
* PostgreSQL
* RabbitMQ
* Redis


Install
^^^^^^^

.. code-block:: bash

    # Ubuntu, begin
    $ sudo apt-get install git
    # Ubuntu, end

    # OSX, begin
    $ sudo port install postgresql95-server rabbitmq-server redis git py27-pip py27-virtualenv libyaml
    # OSX, end

    $ git clone https://github.com/ZenSecurity/waspc_project.git
    $ cd waspc_project

    # Ubuntu, begin
    $ sudo ./install_os_dependencies.sh install
    $ ./install_python_dependencies.sh
    # Ubuntu, end

    # OSX, begin
    $ virtualenv venv --python=`which python2`
    $ source venv/bin/activate
    $(venv) export PATH="/opt/local/lib/postgresql95/bin/:$PATH" ARCHFLAGS="-arch x86_64" LDFLAGS="-L/opt/local/lib" CFLAGS="-I/opt/local/include"
    $(venv) pip install -r requirements.txt --verbose
    # OSX, end

Create a local PostgreSQL database with granted user

.. code-block:: bash

    # Ubuntu, begin
    $(venv) sudo /etc/init.d/postgresql start
    $(venv) sudo su postgres
    $(venv) psql -c 'CREATE DATABASE waspc'
    $(venv) psql -c "CREATE USER waspc WITH PASSWORD 'waspc'"
    $(venv) psql -c 'GRANT ALL PRIVILEGES ON DATABASE waspc to waspc'
    $(venv) exit
    # Ubuntu, end

    # OSX, begin
    $(venv) sudo mkdir -p /opt/local/var/db/postgresql95/defaultdb
    $(venv) sudo chown postgres:postgres /opt/local/var/db/postgresql95/defaultdb
    $(venv) sudo su postgres
    $(venv) cd ~/defaultdb/
    $(venv) /opt/local/lib/postgresql95/bin/initdb -D /opt/local/var/db/postgresql95/defaultdb
    $(venv) /opt/local/lib/postgresql95/bin/pg_ctl -D /opt/local/var/db/postgresql95/defaultdb -l logfile start
    $(venv) export PATH="/opt/local/lib/postgresql95/bin/:$PATH"
    $(venv) psql -c 'CREATE DATABASE waspc'
    $(venv) psql -c "CREATE USER waspc WITH PASSWORD 'waspc'"
    $(venv) psql -c 'GRANT ALL PRIVILEGES ON DATABASE waspc to waspc'
    $(venv) exit
    # OSX, end

Start RabbitMQ server

.. code-block:: bash

    # Ubuntu, begin
    $(venv) sudo /etc/init.d/rabbitmq-server start
    # Ubuntu, end

    # OSX, begin
    $(venv) sudo port load rabbitmq-server
    # OSX, end

Start Redis server

.. code-block:: bash

    # Ubuntu, begin
    $(venv) sudo /etc/init.d/redis-server start
    # Ubuntu, end

    # OSX, begin
    $(venv) sudo port load redis
    # OSX, end

Run ``migrate`` on your new database

.. code-block:: bash

    $(venv) python manage.py migrate

Run ``collectstatic`` for collecting static files in one place

.. code-block:: bash

    $(venv) python manage.py collectstatic

To create an **superuser account**, use this command

.. code-block:: bash

    $(venv) python manage.py createsuperuser

You can now run the ``runserver`` command

.. code-block:: bash

    $(venv) python manage.py runserver

Open up your browser to http://127.0.0.1:8000/ to see the waspc running locally.

Celery
^^^^^^
This app comes with Celery.

To run a celery worker:

.. code-block:: bash

    $(venv) python manage.py celery worker -P processes -Q scanner,monitoring -l INFO -B
