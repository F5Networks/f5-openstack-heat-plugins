.. _home:

F5 OpenStack Heat Plugins
=========================

.. raw:: html

    <script async defer src="https://f5-openstack-slack.herokuapp.com/slackin.js"></script>

Overview
--------
This repository houses all of F5®'s `Openstack Heat <https://wiki.openstack.org/wiki/Heat>`__
resource plugins. F5's Heat plugins can be used to orchestrate BIG-IP® LTM® services
in your OpenStack environment.

Releases and Versions
---------------------
The current release, v |release|, supports the OpenStack |openstack| release.

Please see `F5 OpenStack Releases, Versioning, and Support Matrix <http://f5-openstack-docs.readthedocs.org/en/latest/releases_and_versioning.html>`_ for additional information about F5's OpenStack plugins, versioning, and BIG-IP compatibility.

Before You Begin
----------------

Before you begin, please note the following:

* The F5 Heat plugins must be installed on the same machine as the Heat engine service in your stack.
* You may need to use ``sudo`` to execute some of the installation and/or configuration commands.
* You will need to install the Python tool ``pip`` on your machine.

    .. code-block:: shell

        $ yum install python-pip \\ CentOS
        $ apt-get install python-pip \\ Ubuntu

* If you are installing a pre-release version of the package with pip, you will need to use the ``--pre`` option.

Installation
------------

.. note::

    Once the plugins are installed, you will need to tell the Heat engine service where to find them. We recommend that you either install the plugins, or link them, to a location where the Heat engine already expects to find them. The default location for Heat plugins is :file:`/usr/lib/heat`.

    If you wish to install the plugins in a different location, update the
    ``plugin_dirs`` section of the Heat configuration file - :file:`/etc/heat/heat.conf` - accordingly.

    Please remember that your installation may differ (sometimes greatly) from what we show below.

CentOS
~~~~~~

1. Install the F5 Heat plugins.

    .. code-block:: shell

        $ sudo pip install f5-openstack-heat-plugins

2. Make the Heat plugins directory (**NOTE:** this may already exist).

    .. code-block:: shell

        $ sudo mkdir -p /usr/lib/heat

3. Create a link to the F5 plugins in the Heat plugins directory.

    .. code-block:: shell

        $ sudo ln -s /usr/lib/python2.7/site-packages/f5_heat /usr/lib/heat/f5_heat

4. Restart the Heat engine service.

    .. code-block:: shell

        $ sudo systemctl restart openstack-heat-engine.service


Ubuntu
~~~~~~

1. Install the F5 Heat plugins.

    .. code-block:: shell

        $ sudo pip install f5-openstack-heat-plugins

2. Make the Heat plugins directory (**NOTE:** this may already exist).

    .. code-block:: shell

        $ sudo mkdir -p /usr/lib/heat

3. Create a link to the F5 plugins in the Heat plugins directory.

    .. code-block:: shell

        $ sudo ln -s /usr/local/lib/python2.7/dist-packages/f5_heat /usr/lib/heat

4. Restart the Heat engine service.

    .. code-block:: shell

        $ sudo service heat-engine restart


Usage
-----
The objects defined by the F5 Heat plugins can be used in Heat templates to orchestrate F5 services in an OpenStack cloud. The sample Heat template below does the following:

* identifies the BIG-IP we want to configure
* provides login credentials for an admin user on the BIG-IP
* identifies the partition on the BIG-IP where the objects we want to create should be placed
* identifies an iApp® template to use to deploy/manage BIG-IP services

The first two resources defined here are required to deploy any object on BIG-IP VE.

* :py:mod:`F5BigIPDevice` identifies and authenticates to the BIG-IP
* :py:mod:`F5SysPartition` identifies the partition on the BIG-IP in which objects will be placed (``Common`` is the default partition).

These two requirements will be linked with the obects we intend to configure (iAppTemplate, iAppService) by calling the 'get_resource' intrinsic function.

.. topic:: Sample Heat template using objects defined by the F5 Heat plugins.

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 9, 12, 14, 17, 18, 22, 25, 26

        resources:
          bigip:
            type: F5::BigIP::Device
            properties:
              ip: 10.0.0.1 # All properties can be passed in as parameters
              username: admin
              password: admin # The password can be passed in as a hidden field
          partition:
            type: F5::Sys::Partition
            properties:
              name: Common # Put these objects in the existing Common partition
              bigip_server: { get_resource: bigip } # Create dependency on bigip
          iapp_template:
            type: F5::Sys::iAppTemplate
            properties:
              name: test_template
              bigip_server: { get_resource: bigip } # Depends on bigip resource
              partition: { get_resource: partition} # Depends on partition as well
              full_template:
                get_file: iapps/full_template.tmpl
          iapp_service:
            type: F5::Sys::iAppService
            properties:
              name: test_service
              bigip_server: { get_resource: bigip }
              partition: { get_resource: partition }
              template_name: test_template # Must match the name in iapp_template resource


.. tip::

    See the `F5 Heat templates <https://github.com/F5Networks/f5-openstack-heat>`_ repo on GitHub for additional examples, or peruse the `documentation <http://f5-openstack-heat.readthedocs.org/en/latest/>`_.

API Documentation
-----------------
.. warning::

    The API documentation is under development. Check back often to see what modules have been updated.

.. toctree::
   :maxdepth: 4

   apidoc/modules.rst



