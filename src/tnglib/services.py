# Copyright (c) 2015 SONATA-NFV, 2017 5GTANGO
# ALL RIGHTS RESERVED.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Neither the name of the SONATA-NFV, 5GTANGO
# nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
# This work has been performed in the framework of the SONATA project,
# funded by the European Commission under Grant number 671517 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the SONATA
# partner consortium (www.sonata-nfv.eu).
#
# This work has been performed in the framework of the 5GTANGO project,
# funded by the European Commission under Grant number 761493 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the 5GTANGO
# partner consortium (www.5gtango.eu).

import requests
import logging
import json
import time
import os
import yaml
import tnglib.env as env

LOG = logging.getLogger(__name__)


def get_service_descriptors():
    """Returns info on all available service descriptors.

    :returns: A list. [0] is a bool with the result. [1] is a list of 
        dictionaries. Each dictionary contains an nsd.
    """

    # get current list of service descriptors
    resp = requests.get(env.service_descriptor_api, timeout=env.timeout)

    if resp.status_code != 200:
        LOG.debug("Request for service descriptors returned with " +
                  (str(resp.status_code)))
        return False, []

    services = json.loads(resp.text)

    services_res = []
    for service in services:
        dic = {'descriptor_uuid': service['uuid'],
               'name': service['nsd']['name'],
               'version': service['nsd']['version'],
               'created_at': service['created_at']}
        LOG.debug(str(dic))
        services_res.append(dic)

    return True, services_res


def get_service_descriptor(service_descriptor_uuid):
    """Returns info on a specific service descriptor.

    :param service_descriptor_uuid: uuid of the nsd.

    :returns: A list. [0] is a bool with the result. [1] is a dictionary 
        containing an nsd.
    """

    # get service info
    url = env.service_descriptor_api + '/' + service_descriptor_uuid
    resp = requests.get(url,
                        timeout=env.timeout)

    if resp.status_code != 200:
        LOG.debug("Request for service descriptor returned with " +
                  (str(resp.status_code)))
        return False, json.loads(resp.text)

    return True, json.loads(resp.text)


def get_service_instances():
    """Returns info on all available service instances.

    :returns: A list. [0] is a bool with the result. [1] is a list of 
        dictionaries. Each dictionary contains an nsr.
    """

    # get current list of service instances
    resp = requests.get(env.service_instance_api, timeout=env.timeout)

    if resp.status_code != 200:
        LOG.debug("Request for service instances returned with " +
                  (str(resp.status_code)))
        return False, []

    services = json.loads(resp.text)

    services_res = []
    for service in services:
        if 'instance_name' not in service.keys():
            service['instance_name'] = ''
        if service['instance_name'] is None:
            service['instance_name'] = ''
        dic = {'instance_uuid': service['uuid'],
               'name': service['instance_name'],
               'status': service['status'],
               'created_at': service['created_at']}
        LOG.debug(str(dic))
        services_res.append(dic)

    return True, services_res


def get_service_instance(service_instance_uuid):
    """Returns info on a specific service instance.

    :param service_instance_uuid: uid of nsr.

    :returns: A list. [0] is a bool with the result. [1] is a dictionary 
        containing an nsr.
    """

    # get service instance info
    url = env.service_instance_api + '/' + service_instance_uuid
    resp = requests.get(url,
                        timeout=env.timeout)

    if resp.status_code != 200:
        LOG.debug("Request for service instance returned with " +
                  (str(resp.status_code)))
        return False, json.loads(resp.text)

    return True, json.loads(resp.text)
