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


class F5LTMVirtualServer(resource.Resource, F5BigIPMixin):
    '''Manages creation of an F5® Virtual Server Resource.'''

    PROPERTIES = (
        NAME,
        BIGIP_SERVER,
        PARTITION,
        IP,
        PORT,
        DEFAULT_POOL,
        VLANS
    ) = (
        'name',
        'bigip_server',
        'partition',
        'ip',
        'port',
        'default_pool',
        'vlans'
    )

    properties_schema = {
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('Name of the pool resource.'),
            required=True
        ),
        BIGIP_SERVER: properties.Schema(
            properties.Schema.STRING,
            _('Reference to the BigIP Server resource.'),
            required=True
        ),
        PARTITION: properties.Schema(
            properties.Schema.STRING,
            _('Reference to the partition resources.'),
            required=True
        ),
        IP: properties.Schema(
            properties.Schema.STRING,
            _('The address of the virtual IP.'),
            required=True
        ),
        PORT: properties.Schema(
            properties.Schema.INTEGER,
            _('The port used for the virtual address.'),
            required=True
        ),
        DEFAULT_POOL: properties.Schema(
            properties.Schema.STRING,
            _('The pool to be associated with this virtual server.'),
        ),
        VLANS: properties.Schema(
            properties.Schema.LIST,
            _('VLAN to use for this virtual server.')
        )
    }

    @f5_common_resources
    def handle_create(self):
        '''Create the BigIP Virtual Server resource on the given device.

        :raises: ResourceFailure exception
        '''

        destination = '/{0}/{1}:{2}'.format(
            self.partition_name,
            self.properties[self.IP],
            self.properties[self.PORT]
        )
        create_kwargs = {
            'name': self.properties[self.NAME],
            'partition': self.partition_name,
            'destination': destination,
            'sourceAddressTranslation': {'type': 'automap'}
        }

        if self.properties[self.DEFAULT_POOL]:
            create_kwargs['pool'] = self.properties[self.DEFAULT_POOL]

        if self.properties[self.VLANS]:
            create_kwargs['vlans'] = self.properties[self.VLANS]
            create_kwargs['vlansEnabled'] = True

        try:
            self.bigip.ltm.virtuals.virtual.create(**create_kwargs)
        except Exception as ex:
            raise exception.ResourceFailure(ex, None, action='CREATE')

    @f5_common_resources
    def handle_delete(self):
        '''Delete the BigIP Virtual Server resource on the given device.

        :raises: ResourceFailure exception
        '''
        if self.bigip.ltm.virtuals.virtual.exists(
                name=self.properties[self.NAME],
                partition=self.partition_name
        ):
            try:
                loaded_pool = self.bigip.ltm.virtuals.virtual.load(
                    name=self.properties[self.NAME],
                    partition=self.partition_name
                )
                loaded_pool.delete()
            except Exception as ex:
                raise exception.ResourceFailure(ex, None, action='DELETE')
        return True


def resource_mapping():
    return {'F5::LTM::VirtualServer': F5LTMVirtualServer}
