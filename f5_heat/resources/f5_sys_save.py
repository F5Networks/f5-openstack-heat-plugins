# coding=utf-8
#
# Copyright 2016 F5 Networks Inc.
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

from common.mixins import f5_bigip
from common.mixins import F5BigIPMixin


class F5SysSave(resource.Resource, F5BigIPMixin):
    '''Save the device configuration.'''

    PROPERTIES = (
        BIGIP_SERVER
    ) = (
        'bigip_server'
    )

    properties_schema = {
        BIGIP_SERVER: properties.Schema(
            properties.Schema.STRING,
            _('Reference to the BigIP Server resource.'),
            required=True
        )
    }

    @f5_bigip
    def handle_create(self):
        '''Save the configuration on the BIG-IP® device.

        :raises: ResourceFailure exception
        '''

        try:
            self.bigip.tm.sys.config.exec_cmd('save')
        except Exception as ex:
            raise exception.ResourceFailure(ex, None, action='CREATE')

    @f5_bigip
    def handle_delete(self):
        '''Delete save resource, which has no communication with the device.'''

        return True


def resource_mapping():
    return {'F5::Sys::Save': F5SysSave}
