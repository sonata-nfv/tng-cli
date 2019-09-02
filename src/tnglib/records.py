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

import logging
import json
import time
import os
import yaml
import tnglib.env as env

LOG = logging.getLogger(__name__)


def get_ips_from_vnfr(vnfr):
    """Returns info on the ip addresses in a vnfr, per vdu.

    :returns: A tuple. [0] is a bool with the result. [1] is a dictionary
              with a key for each VDU. The value is a list of dictionaries.
              Each dictionary has a type key, indicating which type of id,
              and an ip field containing the ip.
    """

    # Check if the VNFR only contains VM based network functions.
    if 'virtual_deployment_units' not in vnfr.keys():
        return False, 'Not a VM based VNFR'

    res = {}
    # Loop over the vdu's
    for vdu in vnfr['virtual_deployment_units']:
        res[vdu['id']] = []

        for cp in vdu['vnfc_instance'][0]['connection_points']:
            res[vdu['id']].append({'id': cp['id'],
                                  'ip': cp['interface']['address']})

    return True, res


