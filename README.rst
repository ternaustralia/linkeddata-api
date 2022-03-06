
linkeddata_api
==============

A set of web APIs to power TERN's `Linked Data Services <https://linkeddata.tern.org.>`_ website.

..

    API docs at: https://linkeddata.tern.org.au/api

This project was bootstrapped with TERN's `flask-cookiecutter <https://bitbucket.org/terndatateam/flask-cookiecutter/src/master/>`_.

Installation
============

.. code:: bash

    pip install linkeddata_api


Configuration
=============

The application can configured like any other Flask application.

First it will load the bundled `settings.py` file to configure sensible defaults.
Please see `settings.py` and https://terndatateam.bitbucket.io/flask_tern/ for details.

Next it will look for an environment variable `LINKEDDATA_API_SETTINGS`. This environment variable
should point to a python file which will be loaded as well. The format is exactly the same as in `settings.py` .

This project uses ``flask_tern``. Be sure to check documentation and code https://bitbucket.org/terndatateam/flask_tern .

Flask-Cors: https://flask-cors.readthedocs.io/en/latest/


Development
===========

Clone the source code and cd into the directory of your local copy.
You may want to adapt settings in .flaskenv

.. code:: bash

    # install project in editable mode
    pip install -e '.[testing,docs]'
    # to run tests use
    pytest
    # coverage report
    pytest --cov --cov-report=html


The same can be done within a docker environment. The following is a simple example using alpine.

.. code:: bash

    docker run --rm -it -p 5000:5000 -v "$(pwd)":/linkeddata_api -w /linkeddata_api alpine:3.10 sh
    # install python in binary libs in container
    apk add python3 py3-cryptography
    # install pkg in container
    pip3 install -e '.[testing]'
    # run tests inside container
    pytest
    pytest --cov --cov-report=html


Run flask development server.

.. code:: bash

    # locally
    flask run
    # within container
    flask run -h 0.0.0.0

The app can then be accessed at http://localhost:5000


Contact
-------

| Edmond Chuc
| e.chuc@uq.edu.au