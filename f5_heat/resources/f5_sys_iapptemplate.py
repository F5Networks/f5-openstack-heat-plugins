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

from heat.common import exception
from heat.common.i18n import _
from heat.engine import properties
from heat.engine import resource
from f5.bigip.bigip import BigIP


class F5SysiAppTemplate(resource.Resource):
    '''Manages creation of an iApp resource on the BigIP device.'''

    PROPERTIES = (
        NAME,
        BIGIP_SERVER,
        BIGIP_USERNAME,
        BIGIP_PASSWORD,
        IMPLEMENTATION,
        PRESENTATION,
        HELP
    ) = (
        'name',
        'bigip_server',
        'bigip_username',
        'bigip_password',
        'implementation',
        'presentation',
        'help'
    )

    properties_schema = {
        NAME: properties.Schema(
            properties.Schema.STRING,
            _('Name of the template.'),
            required=True
        ),
        BIGIP_SERVER: properties.Schema(
            properties.Schema.STRING,
            _('IP address of BigIP device.'),
            required=True
        ),
        BIGIP_USERNAME: properties.Schema(
            properties.Schema.STRING,
            _('Username to use to login to the BigIP.'),
            required=True
        ),
        BIGIP_PASSWORD: properties.Schema(
            properties.Schema.STRING,
            _('Password to use to login to the BigIP.'),
            required=True
        ),
        IMPLEMENTATION: properties.Schema(
            properties.Schema.STRING,
            _('Implementation section of the template.'),
            required=True
        ),
        PRESENTATION: properties.Schema(
            properties.Schema.STRING,
            _('Presentation section of the template.'),
            required=True
        ),
        HELP: properties.Schema(
            properties.Schema.STRING,
            _('Help section of the template.'),
        )
    }

    def __init__(self, name, definition, stack):
        '''Initializes the BigIP object for use throughout this class.

        :param string name: resource name
        :param definition: resource definition from heat
        :param stack: current heat stack object
        :raises: Generic exception # TODO Change to proper exception
        '''

        super(F5SysiAppTemplate, self).__init__(name, definition, stack)
        try:
            self.bigip = BigIP(
                self.properties[self.BIGIP_SERVER],
                self.properties[self.BIGIP_USERNAME],
                self.properties[self.BIGIP_PASSWORD]
            )
        except Exception as ex:
            raise Exception('Failed initializing BigIP object: {}'.format(ex))

    def build_iapp_dict(self):
        '''Build dictionary for posting to BigIP.

        :returns: dictionary of template information
        '''

        sections = {
            'implementation': self.properties[self.IMPLEMENTATION] or '',
            'presentation': self.properties[self.PRESENTATION] or ''
        }
        definition = {'definition': sections}
        template = {'name': self.properties[self.NAME], 'actions': definition}
        return template

    def handle_create(self):
        '''Create the template on the BigIP.

        :raises: ResourceFailure
        '''

        template_dict = self.build_iapp_dict()
        try:
            self.bigip.iapp.create_template(
                name=self.properties[self.NAME],
                template=template_dict
            )
        except exception as ex:
            raise exception.ResourceFailure(ex, None, action='CREATE')

    def handle_delete(self):
        '''Delete the iApp Template on the BigIP.

        :raises: ResourceFailure
        '''

        try:
            self.bigip.iapp.delete_template(
                self.properties[self.NAME]
            )
        except Exception as ex:
            raise exception.ResourceFailure(ex, None, action='DELETE')


def resource_mapping():
    return {'F5::Sys::iAppTemplate': F5SysiAppTemplate}
