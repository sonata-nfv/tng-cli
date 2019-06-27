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

def get_test_results():
    """Returns info on all available tests results.

    :returns: A list. [0] is a bool with the result. [1] is a list of 
        dictionaries. Each dictionary contains a result.
    """

    # get current list of tests results
    resp = requests.get(env.test_results_api,
                        timeout=env.timeout,
                        headers=env.header)

    if resp.status_code != 200:
        LOG.debug("Request for test results returned with " +
                  (str(resp.status_code)))
        return False, []

    tests = json.loads(resp.text)

    tests_res = []
    for test in tests:
        dic = {'uuid': test['uuid'],
               'instance_uuid': test['instance_uuid'],
               'package_id': test['package_id'],
               'service_uuid': test['service_uuid'],
               'test_uuid': test['test_uuid'],
               #'test_instance_uuid': test['test_instance_uuid'],
               'status': test['status'],
               'created_at': test['created_at']}
        LOG.debug(str(dic))
        tests_res.append(dic)

    return True, tests_res


def get_test_result(uuid):
    """Returns info on a specific test result.

    :param uuid: uuid of test.

    :returns: A list. [0] is a bool with the result. [1] is a dictionary 
        containing a test.
    """

    # get service instance info
    url = env.test_results_api + '/' + uuid
    resp = requests.get(url,
                        timeout=env.timeout,
                        headers=env.header)

    if resp.status_code != 200:
        LOG.debug("Request for test returned with " +
                  (str(resp.status_code)))
        return False, json.loads(resp.text)

    return True, json.loads(resp.text)

def get_test_uuid_by_instance_uuid(instance_uuid):
    """Returns the test_uuid on a specific test result filtering by instance_uuid.

    :param uuid: instance uuid.

    :returns: A list. [0] is a bool with the result. [1] is a list of
        dictionaries. Each dictionary contains a test_uuid.
    """

    # get current list of tests results
    resp = requests.get(env.test_results_api,
                        timeout=env.timeout,
                        headers=env.header)

    if resp.status_code != 200:
        LOG.debug("Request for test results returned with " +
                  (str(resp.status_code)))
        return False, []

    tests = json.loads(resp.text)

    tests_uuids = []

    for test in tests:
        if test['instance_uuid'] == instance_uuid:
            dic = {'uuid': test['uuid']}

            LOG.debug(str(dic))
            tests_uuids.append(dic)

    return True, tests_uuids