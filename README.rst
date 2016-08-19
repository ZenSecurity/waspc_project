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

    # OSX, begin
    $ sudo port install git postgresql95-server rabbitmq-server redis py27-pip py27-virtualenv libyaml
    # OSX, end

    $ curl -L https://github.com/ZenSecurity/waspc_project/archive/master.tar.gz > waspc_project-master.tar.gz
    $ tar -zxvf waspc_project-master.tar.gz
    $ cd waspc_project-master

    # Ubuntu, begin
    $ sudo ./install_os_dependencies.sh install
    $ ./install_python_dependencies.sh
    # Ubuntu, end

    # OSX, begin
    $ virtualenv-2.7 venv --python=`which python2` --no-setuptools
    $ source venv/bin/activate
    $(venv) curl https://bootstrap.pypa.io/get-pip.py | python
    $(venv) export PATH="/opt/local/lib/postgresql95/bin/:$PATH" ARCHFLAGS="-arch x86_64" LDFLAGS="-L/opt/local/lib" CFLAGS="-I/opt/local/include"
    $(venv) pip install -r requirements.txt --verbose
    # OSX, end

Create a local PostgreSQL database with granted user

.. code-block:: bash

    # Ubuntu, begin
    $(venv) sudo /etc/init.d/postgresql start
    $(venv) sudo su postgres -c './flushdb.sh'
    # Ubuntu, end

    # OSX, begin
    $(venv) sudo mkdir -p /opt/local/var/db/postgresql95/defaultdb
    $(venv) sudo chown postgres:postgres /opt/local/var/db/postgresql95/defaultdb
    $(venv) sudo su - postgres
    $ cd ~/defaultdb/
    $ export PATH="/opt/local/lib/postgresql95/bin/:$PATH"
    $ initdb -D /opt/local/var/db/postgresql95/defaultdb
    $ pg_ctl -D /opt/local/var/db/postgresql95/defaultdb -l logfile start
    $ exit
    $(venv) ./flushdb.sh
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

Launch
^^^^^^
You can now run your instance with help of supervisord:

.. code-block:: bash

    $(venv) supervisord -c supervisord.conf

Now you need to setup your nginx. Basic example you can see in ``waspc.nginx.conf``.
