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

from common.f5_bigip_connection import F5BigIPConnection


class F5LTMPool(resource.Resource, F5BigIPConnection):
    '''Manages creation of an F5 Resource.'''

    PROPERTIES = (
        NAME,
        BIGIP_SERVER,
        SERVICE_DOWN_ACTION,
        MEMBERS
    ) = (
        'name',
        'bigip_server',
        'service_down_action',
        'members'
    )

    _MEMBER_KEYS = (
        MEMBER_IP, MEMBER_PORT
    ) = (
        'member_ip', 'member_port'
    )

    properties_schema = {
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('Name of the pool resource.'),
            required=True
        ),
        BIGIP_SERVER: properties.Schema(
            properties.Schema.STRING,
            _('Reference to the BigIP server resource.'),
            required=True
        ),
        SERVICE_DOWN_ACTION: properties.Schema(
            properties.Schema.STRING,
            _('Action on service down: reject, drop, or reselect.')
        ),
        MEMBERS: properties.Schema(
            properties.Schema.LIST,
            _('List of pool members associated with this pool.'),
            schema=properties.Schema(
                properties.Schema.MAP,
                schema={
                    MEMBER_IP: properties.Schema(
                        properties.Schema.STRING,
                        _('IP address of the member.'),
                        required=True
                    ),
                    MEMBER_PORT: properties.Schema(
                        properties.Schema.STRING,
                        _('Port the member is listening on.'),
                        required=True
                    )
                }
            )
        )
    }

    def assign_members(self):
        '''Assign members to the pool.

        :raises: ResourceFailure
        '''

        members = self.properties[self.MEMBERS]
        for member in members:
            try:
                self.bigip.pool.add_member(
                    name=self.properties[self.NAME],
                    ip_address=member.get(self.MEMBER_IP),
                    port=member.get(self.MEMBER_PORT)
                )
            except exception as ex:
                raise exception.ResourceFailure(ex, None, action='ADD MEMBERS')

    def handle_create(self):
        '''Create the BigIP Pool resource on the given device.

        :rasies: ResourceFailure
        '''

        self.get_bigip()
        try:
            self.bigip.pool.create(self.properties[self.NAME])
        except exception as ex:
            raise exception.ResourceFailure(ex, None, action='CREATE')

        self.assign_members()
        if self.properties[self.SERVICE_DOWN_ACTION]:
            self.bigip.pool.set_service_down_action(
                self.properties[self.NAME],
                self.properties[self.SERVICE_DOWN_ACTION])
        self.resource_id_set(self.physical_resource_name())

    def handle_delete(self):
        '''Delete the BigIP Pool resource on the given device.

        :raises: ResourceFailure
        '''

        self.get_bigip()
        try:
            self.bigip.pool.delete(self.properties[self.NAME])
        except exception as ex:
            raise exception.ResourceFailure(ex, None, action='DELETE')


def resource_mapping():
    return {'F5::LTM::Pool': F5LTMPool}
