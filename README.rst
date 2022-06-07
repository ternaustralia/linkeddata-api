
TERN Linked Data Services API
=============================

A set of web APIs to power TERN's `Linked Data Services <https://linkeddata.tern.org.>`_ website.

..

    API docs at: https://linkeddata.tern.org.au/api

This project was bootstrapped with TERN's `flask-cookiecutter <https://bitbucket.org/terndatateam/flask-cookiecutter/src/master/>`_.

Installation
------------

.. code:: bash

    pip install linkeddata_api


Configuration
-------------

The application can configured like any other Flask application.

First it will load the bundled `settings.py` file to configure sensible defaults.
Please see `settings.py` and https://terndatateam.bitbucket.io/flask_tern/ for details.

Next it will look for an environment variable `LINKEDDATA_API_SETTINGS`. This environment variable
should point to a python file which will be loaded as well. The format is exactly the same as in `settings.py` .

This project uses ``flask_tern``. Be sure to check documentation and code https://bitbucket.org/terndatateam/flask_tern .

Flask-Cors: https://flask-cors.readthedocs.io/en/latest/


Development
-----------

Build and open this project in Visual Studio Code's devcontainer.

Run tests with coverage:

```
make test-cov-local
```

View the coverage report:

```
make cov-report
```

Run the Flask development server

```
flask run
```


Contact
-------

| Edmond Chuc
| e.chuc@uq.edu.au