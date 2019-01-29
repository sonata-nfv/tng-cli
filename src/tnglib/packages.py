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

def get_packages():
    """
    This function returns info on all available packages
    """

    # get current list of packages
    resp = requests.get(env.pkg_api, timeout=5.0)

    if resp.status_code != 200:
        LOG.debug("Request for packages returned with " +
                  (str(resp.status_code)))
        return False, []

    pkgs = json.loads(resp.text)

    pkg_res = []
    for pkg in pkgs:
        dic = {'package_uuid': pkg['uuid'],
               'name': pkg['pd']['name'],
               'version': pkg['pd']['version'],
               'created_at' : pkg['created_at']}
        LOG.debug(str(dic))
        pkg_res.append(dic)

    return True, pkg_res


def remove_all_packages():
    """
    This function removes all packages from the catalogue
    """

    res = []
    # for each package, delete it
    for pkg in get_packages()[1]:
        res.append(remove_package(pkg['package_uuid']))

    for t in res:
        if not t[0]:
            return False, res

    return True, res


def remove_package(package_uuid):
    """
    This function removes one package from the catalogue
    """

    url = env.pkg_api + '/' + package_uuid

    resp = requests.delete(url, timeout=5.0)
    LOG.debug(package_uuid)
    LOG.debug(str(resp.text))

    if resp.status_code == 204:
        return True, package_uuid
    else:
        return False, json.loads(resp.text)['error']


def upload_package(pkg_path):
    """
    This function uploads a package
    """

    pkg = (os.path.basename(pkg_path), open(pkg_path, 'rb'))

    resp = requests.post(env.pkg_api,
                         files={"package":pkg},
                         timeout=1.0)

    pyld = json.loads(resp.text)
    LOG.debug(pyld)

    if resp.status_code != 200:
        LOG.debug(str(pyld))
        return False, str(pyld)

    pkg_proc_id = pyld['package_process_uuid']
    url = env.pkg_status_api + '/' + pkg_proc_id

    for i in range(10):
        resp = requests.get(url, timeout=5.0)
        pyld = json.loads(resp.text)
        LOG.debug(pyld)
        if resp.status_code != 200:
            return False, str(pyld)

        if 'package_process_status' in pyld:
            status = pyld['package_process_status']
            if status == 'success':
                return True, pyld['package_id']
            elif status == 'failed':
                error = str(pyld["package_metadata"]["error"])
                return False, error
            else:
                return False, "upload status: " + str(status)
        time.sleep(1)

    msg = "Couldn't upload package. Is file really a package?"
    LOG.debug(msg)
    return False, msg