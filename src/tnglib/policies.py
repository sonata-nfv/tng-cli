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


def get_policies():
    """Returns info on all available policiy descriptors.

    :returns: A list. [0] is a bool with the result. [1] is a list of 
        dictionaries. Each dictionary contains a policy descriptor.
    """

    # get current list of policies
    resp = requests.get(env.policy_api, timeout=env.timeout)

    if resp.status_code != 200:
        LOG.debug("Request for policies returned with " +
                  (str(resp.status_code)))
        return False, []

    policies = json.loads(resp.text)

    policies_res = []
    for pol in policies:
        dic = {'policy_uuid': pol['uuid'],
               'name': pol['pld']['name'],
               'service': pol['pld']['network_service']['name'],
               'created_at': pol['created_at']}
        LOG.debug(str(dic))
        policies_res.append(dic)

    return True, policies_res


def get_policy(policy_uuid):
    """Returns info on a specific policy descriptor.

    :param policy_uuid: uuid of a policy descriptor.

    :returns: A list. [0] is a bool with the result. [1] is a dictionary 
        containg a policy descriptor.
    """

    # get policy info
    url = env.policy_api + '/' + policy_uuid
    resp = requests.get(url, timeout=env.timeout)

    if resp.status_code != 200:
        LOG.debug("Request for policy returned with " +
                  (str(resp.status_code)))
        return False, json.loads(resp.text)

    return True, json.loads(resp.text)


def create_policy(path):
    """Uploads a policy descriptor.

    :param path: relative path where policy descriptor is stored.

    :returns: A list. [0] is a bool with the result. [1] is a string containing
        the uuid of the uploaded policy descriptor.
    """

    ext = os.path.splitext(path)[1]

    if ext == '.json':
        template_raw = open(path, 'r')
        template = json.load(template_raw)
    elif ext in ['.yaml', '.yml']:
        template_raw = open(path, 'rb')
        template = yaml.load(template_raw)
    else:
        return False, "Provide json or yaml file"

    resp = requests.post(env.policy_api,
                         json=template,
                         timeout=env.timeout)

    if resp.status_code != 200:
        LOG.debug("Request returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    #uuid = json.loads((json.loads(resp.text)['returnobject']))['uuid']

    #return True, uuid
    message = json.loads(resp.text)['uuid']

    return True, message


def delete_policy(policy_uuid):
    """Deletes a policy descriptor.

    :param policy_uuid: uuid of a policy descriptor.

    :returns: A list. [0] is a bool with the result. [1] is a string containing
        the uuid of the terminated policy descriptor.
    """

    url = env.policy_api + '/' + policy_uuid

    resp = requests.delete(url, timeout=env.timeout)
    LOG.debug(policy_uuid)
    LOG.debug(str(resp.text))

    if resp.status_code == 200:
        return True, policy_uuid
    else:
        return False, json.loads(resp.text)

def define_policy_as_default(policy_uuid,service_uuid):
    """Define a Runtime Policy as default.

    :param policy_uuid: uuid of a policy descriptor.

    :returns: A list. [0] is a bool with the result. [1] is a string containing
        the uuid of the terminated policy descriptor.
    """

    url = env.policy_api + '/default/' + policy_uuid

    data = {'nsid': service_uuid, 'defaultPolicy': True}
    resp = requests.patch(url,
                          json=data,
                          timeout=env.timeout)
  
    if resp.status_code != 200:
        LOG.debug("Request returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    message = json.loads(resp.text)['message']

    return True, message


def attach_policy(policy_uuid, service_uuid, sla_uuid):
    """Attaches a policy to a service and SLA.

    :param policy_uuid: uuid of a policy descriptor.
    :param service_uuid: uuid of a network service.
    :param sla_uuid: uuid of an SLA.

    :returns: A list. [0] is a bool with the result. [1] is a string indicating
        the result.
    """

    data = {'nsid': service_uuid, 'slaid': sla_uuid}
    resp = requests.patch(env.policy_bind_api + '/' + policy_uuid,
                          json=data,
                          timeout=env.timeout)
  
    if resp.status_code != 200:
        LOG.debug("Request returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    message = json.loads(resp.text)['message']

    return True, message

def deactivate_policy(nsr_id):
    """Deactivates an enforced policy.

    :param nsr_id: uuid of a network service record.

    :returns: A list. [0] is a bool with the result. [1] is a string containing
        a message.
    """

    url = env.policy_api + '/deactivate/' + nsr_id

    resp = requests.get(url, timeout=env.timeout)
    LOG.debug(nsr_id)
    LOG.debug(str(resp.text))

    if resp.status_code == 200:
        return True, policy_uuid
    else:
        return False, json.loads(resp.text)

def get_policy_action(nsr_id):
    """Checks if exists any policy action generated for the given nsr_id.

    :param nsr_id: uuid of a network service record.

    :returns: A list. [0] is a bool with the result. [1] is a string containing
        a message.
    """

    url = env.policy_api + '/actions' 

    resp = requests.get(url, timeout=env.timeout)
    LOG.debug(nsr_id)
    LOG.debug(str(resp.text))
    
    actions_string = str(resp.text)

    if resp.status_code == 200:
        return True, nsr_id in actions_string
    else:
        return False, json.loads(resp.text)

