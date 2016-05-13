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

import f5_heat

from setuptools import find_packages
from setuptools import setup


setup(
    name='f5-openstack-heat-plugins',
    description='F5 Networks OpenStack Heat Plugin Library',
    license='Apache License, Version 2.0',
    version=f5_heat.__version__,
    author='F5 Networks',
    author_email='f5_openstack_heat@f5.com',
    url='https://github.com/F5Networks/f5-openstack-heat-plugins/',
    keywords=['F5', 'openstack', 'heat', 'bigip', 'orchestration'],
    install_requires=[
        'f5-sdk >= 0.1.6'
    ],
    packages=find_packages(
        exclude=[
            "*.test",
            "*.test.*",
            "test.*",
            "test_*",
            "test",
            "test*",
            "examples"
        ]
    ),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Intended Audience :: System Administrators',
    ]
)
