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

def get_slice_templates():
    """
    This function returns info on all available slices
    """

    # get current list of slices
    resp = requests.get(env.slice_template_api, timeout=env.timeout)

    if resp.status_code != 200:
        LOG.debug("Request for slices returned with " +
                  (str(resp.status_code)))
        return False, []

    slices = json.loads(resp.text)

    slices_res = []
    for slc in slices:
        dic = {'slice_uuid': slc['uuid'],
               'name': slc['nstd']['name'],
               'version': slc['nstd']['version'],
               'created_at' : slc['created_at']}
        LOG.debug(str(dic))
        slices_res.append(dic)

    return True, slices_res

def get_slice_template(slice_template_uuid):
    """
    This function returns info on a specific slice
    """

    # get slice info
    resp = requests.get(env.slice_template_api + '/' + slice_template_uuid, timeout=env.timeout)

    if resp.status_code != 200:
        LOG.debug("Request for slice returned with " +
                  (str(resp.status_code)))
        return False, json.loads(resp.text)

    return True, json.loads(resp.text)

def get_slice_instances():
    """
    This function returns info on all available slice instances
    """

    # get current list of slices
    resp = requests.get(env.slice_instance_api, timeout=env.timeout)

    if resp.status_code != 200:
        LOG.debug("Request for slices returned with " +
                  (str(resp.status_code)))
        return False, []

    slices = json.loads(resp.text)

    slices_res = []
    for slc in slices:
        dic = {'instance_uuid': slc['uuid'],
               'name': slc['name'],
               'template_uuid': slc['nstId'],
               'created_at' : slc['created_at']}
        LOG.debug(str(dic))
        slices_res.append(dic)

    return True, slices_res

def get_slice_instance(slice_instance_uuid):
    """
    This function returns info on a specific slice instance
    """

    # get slice info
    resp = requests.get(env.slice_instance_api + '/' + slice_instance_uuid, timeout=env.timeout)

    if resp.status_code != 200:
        LOG.debug("Request for slice returned with " +
                  (str(resp.status_code)))
        return False, json.loads(resp.text)

    return True, json.loads(resp.text)

def delete_slice_template(slice_template_uuid):
    """
    This function deletes a specific slice
    """

    # delete slice
    resp = requests.delete(env.slice_template_api + '/' + slice_template_uuid, timeout=env.timeout)

    if resp.status_code != 200:
        LOG.debug("Request for slice removal returned with " +
                  (str(resp.status_code)))
        return False, json.loads(resp.text)

    return True, slice_template_uuid

def create_slice_template(path):
    """
    This function generates a slice template
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

    resp = requests.post(env.slice_template_api,
                         json = template,
                         timeout=env.timeout)
  
    if resp.status_code != 201:
        LOG.debug("Request for creating slice template returned with " + (str(resp.status_code)))
        error = resp.text
        return False, error

    uuid = json.loads(resp.text)['uuid']

    return True, uuid