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
import tnglib.env as env

LOG = logging.getLogger(__name__)

def get_test_descriptors():
    """Returns info on all available test descriptors.

    :returns: A list. [0] is a bool with the result. [1] is a list of
        dictionaries. Each dictionary contains a test descriptor.
    """

    # get current list of test descriptors
    resp = requests.get(env.test_descriptors_api,
                        timeout=env.timeout,
                        headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request for test descriptors returned with " +
                  (str(resp.status_code)))
        return False, []

    descriptors = json.loads(resp.text)

    descriptors_res = []
    for descriptor in descriptors:

        platforms = ""
        for platform in descriptor['testd']['service_platforms']:
            print (platform)
            if platforms == "":
                platforms = platform
            else:
                platforms = platforms + "," + platform

        dic = {'uuid': descriptor['uuid'],
               'name': descriptor['testd']['name'],
               'vendor': descriptor['testd']['vendor'],
               'version': descriptor['testd']['version'],
               'platforms': platforms,
               'status': descriptor['status'],
               'updated_at': descriptor['updated_at']}
        LOG.debug(str(dic))
        descriptors_res.append(dic)

    return True, descriptors_res

def get_test_descriptor(uuid):
    """Returns info on a specific test descriptor.

    :param uuid: uuid of test descriptor.

    :returns: A list. [0] is a bool with the result. [1] is a dictionary
        containing a test descriptor.
    """

    url = env.test_descriptors_api + '/' + uuid
    resp = requests.get(url,
                        timeout=env.timeout,
                        headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request for test descriptor returned with " +
                  (str(resp.status_code)))
        return False, json.loads(resp.text)

    return True, json.loads(resp.text)