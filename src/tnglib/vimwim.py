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

def clean_infrastructure():
    """Delete all vims and wims

    :returns: A list. [0] is a bool with the result.
    """

    vims = get_vims()[1]
    wims = get_wims()[1]

    for wim in wims:
        res = delete_wim(wim['wim_uuid'])
        if not res[0]:
            return res

    for vim in vims:
        res = delete_vim(vim['vim_uuid'])
        if not res[0]:
            return res

    return True, ''

def delete_vim(vim_uuid):
    """Delete a vim.

    :param vim_uuid: uuid of the vim to be deleted.

    :returns: A list. [0] is a bool with the result. [1] is response message.
    """

    url = env.ia_api + '/vims/' + vim_uuid 

    resp = requests.delete(url,
                        timeout=env.timeout,
                        headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request for vims returned with " +
                  (str(resp.status_code)))
        return False, []

    return True, json.loads(resp.text)

def delete_wim(wim_uuid):
    """Delete a wim.

    :param wim_uuid: uuid of the wim to be deleted.

    :returns: A list. [0] is a bool with the result. [1] is response message.
    """

    url = env.ia_api + '/wims/' + wim_uuid 

    resp = requests.delete(url,
                        timeout=env.timeout,
                        headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request for wims returned with " +
                  (str(resp.status_code)))
        return False, []

    return True, json.loads(resp.text)

def get_vim(vim_uuid):
    """Get a vim.

    :param vim_uuid: uuid of the vim.

    :returns: A list. [0] is a bool with the result. [1] is response message.
    """

    url = env.ia_api + '/vims/' + vim_uuid 

    resp = requests.get(url,
                        timeout=env.timeout,
                        headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request for vims returned with " +
                  (str(resp.status_code)))
        return False, []

    return True, json.loads(resp.text)

def get_wim(wim_uuid):
    """Get a wim.

    :param wim_uuid: uuid of the wim.

    :returns: A list. [0] is a bool with the result. [1] is response message.
    """

    url = env.ia_api + '/wims/' + wim_uuid 

    resp = requests.get(url,
                        timeout=env.timeout,
                        headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request for wims returned with " +
                  (str(resp.status_code)))
        return False, []

    return True, json.loads(resp.text)

def get_vims(vim_type=None):
    """Obtain the available Vims.

    :param type: optional type of vim

    :returns: A list. [0] is a bool with the result. [1] is a list of 
        dictionaries. Each dictionary contains a vim.
    """

    # get current list of vims
    url = env.ia_api + '/vims'
    if vim_type:
        url = url + '?type=' + vim_type 
    resp = requests.get(url,
                        timeout=env.timeout,
                        headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request for vims returned with " +
                  (str(resp.status_code)))
        return False, []

    vims = json.loads(resp.text)

    vims_res = []
    for vim in vims:
        dic = {'vim_uuid': vim['uuid'],
               'name': vim['name'],
               'type': vim['type']}
        vims_res.append(dic)

    return True, vims_res

def get_wims(wim_type=None):
    """Obtain the available Wims.

    :param type: optional type of wim

    :returns: A list. [0] is a bool with the result. [1] is a list of 
        dictionaries. Each dictionary contains a wim.
    """

    # get current list of wims
    url = env.ia_api + '/wims'
    if wim_type:
        url = url + '?type=' + wim_type 
    resp = requests.get(url,
                        timeout=env.timeout,
                        headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request for wims returned with " +
                  (str(resp.status_code)))
        return False, []

    wims = json.loads(resp.text)

    wims_res = []
    for wim in wims:
        dic = {'wim_uuid': wim['uuid'],
               'name': wim['name'],
               'type': wim['type']}
        wims_res.append(dic)

    return True, wims_res

def post_vim(vim_type, payload):
    """Post a vim

    :param vim_type: the type of vim
    :param json_payload: the payload as json

    :returns: A list. [0] is a bool with the result. [1] the uuid of the vim.
    """

    # get current list of vims
    url = env.ia_api + '/vims/' + vim_type
    resp = requests.post(url,
                         json=payload,
                         timeout=env.timeout,
                         headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code not in [200, 201]:
        LOG.debug("Request to post vim returned with " +
                  (str(resp.status_code)))
        return False, []

    return True, json.loads(resp.text)

def post_vim_from_file(tag, file=None):
    """Post a vim from file

    :param file: path to the file
    :param tag: name of vim in file

    :returns: A list. [0] is a bool with the result. [1] the uuid of the vim.
    """

    if not file:
        if os.environ.get('INFRA_FILE_PATH'):
            file = os.environ.get('INFRA_FILE_PATH')
        else:
            return False, 'No infrastructure file'

    data = yaml.load(open(file, 'r'))

    return post_vim(data[tag]['type'], data[tag]['payload'])

def get_available_vim_tags(file=None):
    """return the available vim tags

    :param file: path to the file

    :returns: A list. [0] is a bool with the result. [1] list of tags.
    """

    if not file:
        if os.environ.get('INFRA_FILE_PATH'):
            file = os.environ.get('INFRA_FILE_PATH')
        else:
            return False, 'No infrastructure file'

    data = yaml.load(open(file, 'r'))

    return True, list(data.keys())
