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

from tnglib.packages import *
from tnglib.slas import *
from tnglib.general import *
from tnglib.services import *
from tnglib.functions import *
from tnglib.policies import *
from tnglib.requests import *
from tnglib.slices import *
from tnglib.logs import *
from tnglib.tests import *
from tnglib.records import *
from tnglib.env import set_sp_path, get_sp_path, set_timeout, add_token_to_header, get_return_header, set_return_header
from tnglib.plans import *
from tnglib.results import *
from tnglib.monitor import *
from tnglib.vimwim import *
from tnglib.recommendations import *

set_sp_path('localhost')
