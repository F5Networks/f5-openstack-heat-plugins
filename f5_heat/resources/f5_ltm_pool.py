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

from common.mixins import f5_common_resources
from common.mixins import F5BigIPMixin


class F5LTMPool(resource.Resource, F5BigIPMixin):
    '''Manages creation of an F5® Resource.'''

    PROPERTIES = (
        NAME,
        BIGIP_SERVER,
        PARTITION,
        SERVICE_DOWN_ACTION,
        MEMBERS
    ) = (
        'name',
        'bigip_server',
        'partition',
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
        PARTITION: properties.Schema(
            properties.Schema.STRING,
            _('Reference to partition resource.'),
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

    @f5_common_resources
    def _assign_members(self):
        '''Assign members to the pool.

        :raises: ResourceFailure
        '''

        members = self.properties[self.MEMBERS]
        for member in members:
            member_ip = member[self.MEMBER_IP]
            member_port = member[self.MEMBER_PORT]
            member_name = '{0}:{1}'.format(member_ip, member_port)
            try:
                loaded_pool = self.bigip.ltm.pools.pool.load(
                    name=self.properties[self.NAME],
                    partition=self.partition_name
                )
                loaded_pool.members_s.members.create(
                    name=member_name,
                    partition=self.partition_name,
                    address=member_ip
                )
            except Exception as ex:
                raise exception.ResourceFailure(ex, None, action='ADD MEMBERS')

    @f5_common_resources
    def handle_create(self):
        '''Create the BigIP Pool resource on the given device.

        :rasies: ResourceFailure
        '''

        create_kwargs = {
            'name': self.properties[self.NAME],
            'partition': self.partition_name
        }
        if self.properties[self.SERVICE_DOWN_ACTION]:
            create_kwargs['service_down_action'] = \
                self.properties[self.SERVICE_DOWN_ACTION]

        try:
            self.bigip.ltm.pools.pool.create(**create_kwargs)
        except Exception as ex:
            raise exception.ResourceFailure(ex, None, action='CREATE')

        if self.properties[self.MEMBERS]:
            self._assign_members()
        self.resource_id_set(self.physical_resource_name())

    @f5_common_resources
    def handle_delete(self):
        '''Delete the BigIP Pool resource on the given device.

        :raises: ResourceFailure
        '''

        if self.bigip.ltm.pools.pool.exists(
                name=self.properties[self.NAME],
                partition=self.partition_name
        ):
            try:
                loaded_pool = self.bigip.ltm.pools.pool.load(
                    name=self.properties[self.NAME],
                    partition=self.partition_name
                )
                loaded_pool.delete()
            except Exception as ex:
                raise exception.ResourceFailure(ex, None, action='DELETE')
        return True


def resource_mapping():
    return {'F5::LTM::Pool': F5LTMPool}
