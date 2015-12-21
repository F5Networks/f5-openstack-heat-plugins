# Copyright 2015 F5 Networks Inc.
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

from heat.common.i18n import _
from heat.engine import properties
from heat.engine import resource


class F5BigIP(resource.Resource):
    '''Holds BigIP server, username, and password.'''

    PROPERTIES = (
        BIGIP_SERVER
    ) = (
        'bigip_server'
    )

    properties_schema = {
        BIGIP_SERVER: properties.Schema(
            properties.Schema.STRING,
            _('IP address of BigIP device.'),
            required=True
        )
    }

    def handle_create(self):
        '''Create the BigIP resource.'''
        pass

    def handle_delete(self):
        '''Delete BigIP resource.'''
        pass


def resource_mapping():
    return {'F5::BigIP': F5BigIP}
