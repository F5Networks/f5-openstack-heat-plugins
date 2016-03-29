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


class F5SysPartition(resource.Resource, F5BigIPMixin):
    '''Manages creation of an F5® Virtual Server Resource.'''

    PROPERTIES = (
        NAME,
        BIGIP_SERVER,
        NAME,
        SUBPATH
    ) = (
        'name',
        'bigip_server',
        'name',
        'subpath'
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
        SUBPATH: properties.Schema(
            properties.Schema.STRING,
            _('Subpath for the folder or parition.'),
            default='/'
        )
    }

    def get_partition_name(self):
        '''Retrieve partition name from this resource.

        :returns: string of partition name
        '''

        return self.properties[self.NAME]

    @f5_bigip
    def handle_create(self):
        '''Create the BIG-IP® Virtual Server resource on the given device.

        If the 'Common' partition was specified, do not create, as it exists
        on the BIG-IP® by default.

        :raises: ResourceFailure exception
        '''

        if self.properties[self.NAME] != 'Common':
            try:
                self.bigip.sys.folders.folder.create(
                    name=self.properties[self.NAME],
                    subPath=self.properties[self.SUBPATH]
                )
            except Exception as ex:
                raise exception.ResourceFailure(ex, None, action='CREATE')

    @f5_bigip
    def handle_delete(self):
        '''Delete the BIG-IP® Virtual Server resource on the given device.

        If the 'Common' partition was specified, do not delete, as it exists
        on the BIG-IP® by default.

        :raises: ResourceFailure exception
        '''

        if self.bigip.sys.folders.folder.exists(
                name=self.properties[self.NAME]
        ):
            if self.properties[self.NAME] != 'Common':
                try:
                    loaded_partition = self.bigip.sys.folders.folder.load(
                        name=self.properties[self.NAME]
                    )
                    loaded_partition.delete()
                except Exception as ex:
                    raise exception.ResourceFailure(ex, None, action='DELETE')
        return True


def resource_mapping():
    return {'F5::Sys::Partition': F5SysPartition}
