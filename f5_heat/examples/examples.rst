F5 Heat Plugin Example Templates
================================

Description
===========
The templates in this directory demonstrate how to use F5 Heat resources. A good starting point is the deploy_composite_iapp.yaml Heat template. It shows how to deploy an F5::Sys::iAppCompositeTemplate and F5::Sys::iAppService resource in Heat, which creates an iApp service on the BigIP. An iApp is a specific configuration deployment represented as an executable TCL script. The script is call an iApp Template. There are two ways to deploy iApp Templates with F5's Heat plugins: the first is as shown in deploy_composite_iapp.yaml--F5::Sys::iAppCompositeTemplate, and the other method is a simple dump of the full TCL file into the Heat template--F5::Sys::iAppFullTemplate. Once the template has been created on the BigIP device, it can then be executed to create the iApp Service--F5::Sys::iAppService. Examples of each plugin we support exist in this directory. Feel free to browse around and tweak those parameters and resources to suit your needs.
