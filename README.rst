f5-openstack-heat-plugins
=========================

|travis build| |docs build| |slack badge|

Introduction
------------
This repository houses all of F5®'s OpenStack Heat resource plugins. F5®'s
Heat plugins can be used to orchestrate BIG-IP®  services in your OpenStack environment.

Releases and Versions
---------------------
This branch supports the OpenStack Kilo release.

Please see `F5® OpenStack Releases, Versioning, and Support Matrix <http://f5-openstack-docs.readthedocs.org/en/latest/releases_and_versioning.html>`_ for additional information
 about F5®'s OpenStack plugins and BIG-IP® compatibility.

Documentation
-------------
Project documentation, which includes installation and usage instructions, can
 be found on `Read The Docs <https://f5-openstack-heat-plugins.readthedocs
 .org/en/>`_.

For Developers
--------------

Filing Issues
`````````````
If you find an issue we would love to hear about it. Please let us know by filing an issue in this repository and tell us as much as you can about what you found and how you found it.

Contributing
````````````
See `Contributing <CONTRIBUTING.md>`_.

Build
`````
To make a PyPI package...

.. code:: bash

    $ python setup.py sdist

Test
````
Before you open a pull request, your code must have passing `pytest <http://pytest.org>`_ unit tests. In addition, you should include a set of functional tests written to use a real BIG-IP®  device for testing. Information on how to run our set of tests is included below.

Unit Tests
~~~~~~~~~~
We use pytest for our unit tests.

#. If you haven't already, install requirements.unit.test.txt in your virtual
   environment.

.. code:: shell

   $ pip install hacking pytest pytest-cov
   $ pip install -r requirements.txt

#. Run the tests and produce a coverage report. The ``--cov-report=html`` will create a ``htmlcov/`` directory that you can view in your browser to see the missing lines of code.

.. code:: shell
       $ pip install -r requirements.unit.test.txt

#. | Run the tests and produce a coverage report. The
     ``--cov-report=html`` will
   | create a ``htmlcov/`` directory that you can view in your browser
     to see the
   | missing lines of code.
       py.test --cov f5_heat/resources/test --cov-report=html
       open htmlcov/index.html

Functional Tests
~~~~~~~~~~~~~~~~
Pytest is also used for functional tests

#. If you haven't already, install requirements.func.test.txt in your virtual
   environment.

   .. code:: shell

       $ pip install -r requirements.func.test.txt

#. | Currently, you must modify ``test/functional/test_variables.py`` file to
     provide the proper credentials to Openstack. See that file for more info
     on what is needed. Also remember not to include this file in your pull
     request, since it may contiain sensitive information.

#. | Run the functional tests and pass in arguments to connect to the F5® Device.

   .. code:: shell

       py.test test/functional/ --bigip=<bigip_ip> --bigip-username=<web_login_username> --bigip-passwword=<web_login_password>

Style Checks
~~~~~~~~~~~~
We use the hacking module for our style checks (installed as part of step 1 in the Unit Test section).

.. code:: shell

    $ flake8 ./

Copyright
---------
Copyright 2015-2016 F5 Networks, Inc.

Support
-------
See `Support <SUPPORT.md>`_.

License
-------

Apache V2.0
~~~~~~~~~~~
Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing
permissions and limitations under the License.

Contributor License Agreement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Individuals or business entities who contribute to this project must
have completed and submitted the `F5® Contributor License
Agreement <http://f5-openstack-docs.readthedocs.org/en/latest/cla_landing.html>`__
to Openstack_CLA@f5.com prior to their code submission being included in this
project.


.. |travis build| image:: https://travis-ci.org/F5Networks/f5-openstack-heat-plugins.svg?branch=kilo
    :target: https://travis-ci.org/F5Networks/f5-openstack-heat-plugins

.. |docs build| image:: https://readthedocs.org/projects/f5-openstack-heat-plugins/badge/?version=kilo
    :target: http://f5-openstack-heat-plugins.readthedocs.org/en/latest/?badge=kilo

.. |slack badge| image:: https://f5-openstack-slack.herokuapp.com/badge.svg
    :target: https://f5-openstack-slack.herokuapp.com/
    :alt: Slack
