# coding=utf-8
#
# Copyright 2015-2016 F5 Networks Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from heat.common import exception
from heat.common.i18n import _
from heat.engine import properties
from heat.engine import resource

from f5.multi_device.cluster import ClusterManager
from f5.sdk_exception import F5SDKError


class UpdateNotAllowed(object):
    pass


class F5CmCluster(resource.Resource):
    '''Manages creation of the F5::Cm::Cluster resource.'''

    PROPERTIES = (
        DEVICE_GROUP_NAME,
        DEVICES,
        DEVICE_GROUP_PARTITION,
        DEVICE_GROUP_TYPE
    ) = (
        'device_group_name',
        'devices',
        'device_group_partition',
        'device_group_type'
    )

    properties_schema = {
        DEVICE_GROUP_NAME: properties.Schema(
            properties.Schema.STRING,
            _('Name of the template.'),
            required=True
        ),
        DEVICES: properties.Schema(
            properties.Schema.LIST,
            _('BigIP resource references for devices to cluster.'),
            required=True,
            update_allowed=True
        ),
        DEVICE_GROUP_PARTITION: properties.Schema(
            properties.Schema.STRING,
            _('Partition where device group will be deployed.'),
            default='Common',
            required=True
        ),
        DEVICE_GROUP_TYPE: properties.Schema(
            properties.Schema.STRING,
            _('The type of cluster to create (sync-failover)'),
            default='sync-failover',
            required=True
        )
    }

    def _set_devices(self):
        '''Retrieve the BIG-IP® connection from the F5::BigIP resource.'''

        self.devices = []
        for device in self.properties[self.DEVICES]:
            self.devices.append(
                self.stack.resource_by_refid(device).get_bigip()
            )

    def handle_create(self):
        '''Create the device service group (cluster) of devices.

        :raises: ResourceFailure
        '''

        self._set_devices()
        try:
            cluster_mgr = ClusterManager()
            cluster_mgr.create(
                devices=self.devices,
                device_group_name=self.properties[self.DEVICE_GROUP_NAME],
                device_group_partition=self.properties[
                    self.DEVICE_GROUP_PARTITION
                ],
                device_group_type=self.properties[self.DEVICE_GROUP_TYPE]
            )
        except F5SDKError as ex:
            raise exception.ResourceFailure(ex, None, action='CREATE')

    def handle_delete(self):
        '''Teardown the device service group (cluster).

        :raises: ResourceFailure
        '''

        self._set_devices()
        try:
            cluster_mgr = ClusterManager(
                devices=self.devices,
                device_group_name=self.properties[self.DEVICE_GROUP_NAME],
                device_group_partition=self.properties[
                    self.DEVICE_GROUP_PARTITION
                ],
                device_group_type=self.properties[self.DEVICE_GROUP_TYPE]
            )
            cluster_mgr.teardown()
        except F5SDKError as ex:
            raise exception.ResourceFailure(ex, None, action='DELETE')

        return True


def resource_mapping():
    return {'F5::Cm::Cluster': F5CmCluster}
