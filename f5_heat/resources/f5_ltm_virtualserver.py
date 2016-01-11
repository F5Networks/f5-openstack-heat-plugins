# Copyright 2015-2016-2016 F5 Networks Inc.
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


class F5LTMVirtualServer(resource.Resource, F5BigIPConnection):
    '''Manages creation of an F5 Virtual Server Resource.'''

    PROPERTIES = (
        NAME,
        BIGIP_SERVER,
        IP,
        PORT,
        DEFAULT_POOL
    ) = (
        'name',
        'bigip_server',
        'ip',
        'port',
        'default_pool'
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
        )
    }

    def handle_create(self):
        '''Create the BigIP Virtual Server resource on the given device.

        :raises: ResourceFailure exception
        '''

        self.get_bigip()

        try:
            self.bigip.virtual_server.create(
                name=self.properties[self.NAME],
                ip_address=self.properties[self.IP],
                port=self.properties[self.PORT]
            )
        except Exception as ex:
            raise exception.ResourceFailure(ex, None, action='CREATE')

    def handle_delete(self):
        '''Delete the BigIP Virtual Server resource on the given device.

        :raises: ResourceFailure exception
        '''

        self.get_bigip()

        try:
            self.bigip.virtual_server.delete(name=self.properties[self.NAME])
        except Exception as ex:
            raise exception.ResourceFailure(ex, None, action='DELETE')


def resource_mapping():
    return {'F5::LTM::VirtualServer': F5LTMVirtualServer}
