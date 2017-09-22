F5 Plugins for OpenStack Heat
=============================

.. sidebar:: **OpenStack version:**

   |openstack|

.. raw:: html

   <script async defer src="https://f5-openstack-slack.herokuapp.com/slackin.js"></script>

.. toctree::
   :hidden:
   :maxdepth: 1

version |release|
-----------------

|release-notes|


The F5 Plugins for OpenStack Heat are a set of `OpenStack Heat Resource Plugins`_.
These resource plugins extend the Heat orchestration service for use with F5 BIG-IP devices.

Installation
------------

.. rubric:: Tasks

#. Install ``pip`` (required to install the heat-plugins package).
#. Create the Heat plugins directory -- :file:`/usr/lib/heat`.
   (This may already exist.)
#. Create a link to the F5 Heat plugins in the OpenStack Heat plugins directory
#. Restart the Heat engine service.

.. hint::

   You may need to use :command:`sudo` to install the F5 Heat plugins and/or modify directories.

CentOS
``````

.. code-block:: console

   yum install python-pip
   pip install f5-openstack-heat-plugins
   mkdir -p /usr/lib/heat
   ln -s /usr/lib/python2.7/site-packages/f5_heat /usr/lib/heat/f5_heat
   systemctl restart openstack-heat-engine.service

Ubuntu
``````

.. code-block:: console

   apt-get install python-pip
   pip install f5-openstack-heat-plugins
   mkdir -p /usr/lib/heat
   sudo ln -s /usr/local/lib/python2.7/dist-packages/f5_heat /usr/lib/heat
   sudo service heat-engine restart

Usage
-----

The F5 plugins for OpenStack Heat define objects used to orchestrate F5 services in Heat templates.
The sample Heat template below does the following:

* Identifies the BIG-IP device you want to configure.
* Provides login credentials for an admin user on the BIG-IP device.
* Identifies the BIG-IP partition where you want to create the objects.
* identifies an iApp template you want to use to deploy/manage BIG-IP services (the template must already exist on the BIG-IP device).

Required resources
``````````````````

* :py:class:`F5BigIPDevice` -- identifies and authenticates to the BIG-IP device.
* :py:class:`F5SysPartition` -- identifies the BIG-IP partition in which you want to create objects (``/Common`` is the default partition).

Example
```````

Call the :func:`get_resource` function to link the required resources with the objects you want to configure (iAppTemplate, iAppService).

.. rubric:: Sample Heat template using objects defined by the F5 Heat plugins.

.. tip::

   - You can pass in any properties as parameters.
   - You can pass in secure information, like your BIG-IP login credentials, as a hidden field.


.. code-block:: yaml
   :linenos:
   :emphasize-lines: 3, 9, 11-12, 14, 17, 18, 22, 25, 26

   resources:
    bigip:
      type: F5::BigIP::Device
      properties:
        ip: 1.2.3.4                             # BIG-IP management IP address
        username: admin
        password: admin
    partition:
      type: F5::Sys::Partition
      properties:
        name: Common                            # Put these objects in the /Common partition
        bigip_server: { get_resource: bigip }   # Create dependency on bigip
    iapp_template:
      type: F5::Sys::iAppFullTemplate
      properties:
        name: test_template
        bigip_server: { get_resource: bigip }   # Depends on bigip resource
        partition: { get_resource: partition}   # Depends on partition resource
        full_template:
          get_file: iapps/http_template.tmpl
    iapp_service:
      type: F5::Sys::iAppService
      properties:
        name: test_service
        bigip_server: { get_resource: bigip }
        partition: { get_resource: partition }
        template_name: http                     # Must match an iapp_template name on the BIG-IP device

Related
-------

See the `F5 template library`_ for OpenStack Heat and the `F5 Integration for OpenStack`_.

.. _OpenStack Heat Resource Plugins: https://docs.openstack.org/developer/heat/developing_guides/pluginguide.html
.. _F5 Integration for OpenStack: /cloud/openstack/heat/latest/
.. _F5 template library: /products/templates/openstack-heat/latest/
