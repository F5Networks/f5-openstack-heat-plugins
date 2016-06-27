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

from f5.bigip import ManagementRoot
from heat.common.i18n import _
from heat.engine import properties
from heat.engine import resource
from requests import HTTPError


class BigIPConnectionFailed(HTTPError):
    pass


class F5BigIPDevice(resource.Resource):
    '''Holds BigIP server, username, and password.'''

    PROPERTIES = (
        IP,
        USERNAME,
        PASSWORD
    ) = (
        'ip',
        'username',
        'password'
    )

    properties_schema = {
        IP: properties.Schema(
            properties.Schema.STRING,
            _('IP address of BigIP device.'),
            required=True
        ),
        USERNAME: properties.Schema(
            properties.Schema.STRING,
            _('Username for logging into the BigIP.'),
            required=True
        ),
        PASSWORD: properties.Schema(
            properties.Schema.STRING,
            _('Password for logging into the BigIP.'),
            required=True
        )
    }

    def get_bigip(self):
        return ManagementRoot(
            self.properties[self.IP],
            self.properties[self.USERNAME],
            self.properties[self.PASSWORD]
        )

    def handle_create(self):
        '''Create the BigIP resource.

        Attempt to initialize a bigip connection to test connectivity

        raises: BigIPConnectionFailed
        '''

        try:
            self.get_bigip()
        except HTTPError as ex:
            raise BigIPConnectionFailed(ex)

        self.resource_id_set(self.physical_resource_name())

    def handle_delete(self):
        '''Delete this connection to the BIG-IP® device.'''

        return True


def resource_mapping():
    return {'F5::BigIP::Device': F5BigIPDevice}
