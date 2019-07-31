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
import tnglib.services as services
import logging
import json
import time
import os
import yaml
import tnglib.env as env

LOG = logging.getLogger(__name__)


def get_packages():
    """Returns info on all available packages.

    :returns: A list. [0] is a bool with the result. [1] is a list of 
        dictionaries. Each dictionary contains a package descriptor.
    """

    # get current list of packages
    resp = requests.get(env.pkg_api,
                        timeout=env.timeout,
                        headers=env.header)

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
               'created_at': pkg['created_at']}
        LOG.debug(str(dic))
        pkg_res.append(dic)

    env.set_return_header(resp.headers)
    return True, pkg_res


def remove_all_packages():
    """Removes all packages from the catalogue.

    :returns: A list. [0] is a bool with the result. [1] is a list of
        uuids of packages that were removed.
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
    """Removes one package from the catalogue.

    :param package_uuid: uuid of the package

    :returns: A list. [0] is a bool with the result. [1] is a string 
        with either the uuid or an error message.
    """

    url = env.pkg_api + '/' + package_uuid

    resp = requests.delete(url,
                           timeout=env.timeout,
                           headers=env.header)

    LOG.debug(package_uuid)
    LOG.debug(str(resp.text))

    env.set_return_header(resp.headers)

    if resp.status_code == 204:
        return True, package_uuid
    else:
        return False, json.loads(resp.text)['error']


def package_status(pkg_id):
    """Check the status of the package uploading process. Can be used to
    obtain the duration of the upload.

    :param pkg_id: uuid of the package uploading process

    :returns: A list. [0] is a bool with the result. [1] is a dictionary
        containing metadata of the package.
    """

    url = env.pkg_status_api + '/' + pkg_id

    resp = requests.get(url, timeout=env.timeout, headers=env.header)

    pyld = json.loads(resp.text)
    LOG.debug(pyld)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        return False, str(pyld)

    return True, pyld


def upload_package(pkg_path, url=False, return_process_uuid=False):
    """Uploads a package from file.

    :param pkg_path: relative path to the package that needs uploading, or url
    :param pkg_path: A bool, True if pkg_path is an url
    :param return_process_uuid: A bool, if you want the package_process_uuid
        returned instead of the package_uuid

    :returns: A list. [0] is a bool with the result. [1] is a string containing
        either the uuid of the uploaded package, the process uuid of the package
         or an error message.
    """

    if not url:
        pkg = (os.path.basename(pkg_path), open(pkg_path, 'rb'))

    else:
        pkg = (pkg_path.split('/')[-1], requests.get(pkg_path).content)

    resp = requests.post(env.pkg_api,
                         files={"package": pkg},
                         timeout=env.timeout,
                         headers=env.header)

    pyld = json.loads(resp.text)
    LOG.debug(pyld)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug(str(pyld))
        return False, str(pyld)

    pkg_proc_id = pyld['package_process_uuid']
    url = env.pkg_status_api + '/' + pkg_proc_id

    for i in range(10):
        resp = requests.get(url, timeout=env.timeout, headers=env.header)
        pyld = json.loads(resp.text)
        LOG.debug(pyld)
        if resp.status_code != 200:
            return False, str(pyld)

        if 'package_process_status' in pyld:
            status = pyld['package_process_status']
            if status == 'success':
                if return_process_uuid:
                    return True, pkg_proc_id
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


def get_package(package_uuid):
    """Returns info on a specific package.

    :param package_uuid: the uuid of the package

    :returns: A list. [0] is a bool with the result. [1] is a dictionary 
        containing a package descriptor.
    """

    # get package info
    resp = requests.get(env.pkg_api + '/' + package_uuid,
                        timeout=env.timeout,
                        headers=env.header)

    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request for package returned with " +
                  (str(resp.status_code)))
        return False, json.loads(resp.text)

    return True, json.loads(resp.text)

def map_package_on_service(package_uuid):
    """Return the uuid of a network service based on a package uuid.

    :param package_uuid: the uuid of the package

    :returns: A list. [0] is a bool with the result. [1] is a string 
        containing a nsd uuid.
    """

    status, package_metadata = get_package(package_uuid)

    if not status:
        msg = "Couldn't obtain package metadata"
        return False, msg

    for cnt in package_metadata['pd']['package_content']:
        if '5gtango.nsd' in cnt['content-type']:
            name = cnt['id']['name']
            version = cnt['id']['version']
            vendor = cnt['id']['vendor']

    nsds = services.get_service_descriptors()[1]
    for nsd in nsds:
        if (nsd['name'] == name) and (nsd['version'] == version):
            return True, nsd['descriptor_uuid']

    return False, "Couldn't find associated nsd"