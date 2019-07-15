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

import sys
import argparse
import tnglib
import yaml
import os
import logging
import getpass


LOG = logging.getLogger(__name__)


def run(args=None):
    """
    Entry point.
    Can get a list of args that are then used as input for the CLI arg parser.
    """

    if args is None:
        args = sys.argv[1:]
    parsed_args = parse_args(args)
    return dispatch(parsed_args)


def dispatch(args):
    """
    post process the arguments and link them to specific actions
    """

    # Handle the verbose argument
    init_logger(args.verbose)

    # abort if no subcommand is provided
    if args.subparser_name is None:
        print("Missing subcommand. Type tng-cli -h")
        exit(1)

    # Handle --url argument and set environment
    if args.sp_url:
        tnglib.set_sp_path(args.sp_url)
    else:
        if 'SP_PATH' in os.environ:
            tnglib.set_sp_path(os.environ["SP_PATH"])
        else:
            print("Missing path to SP. Use env SP_PATH or tng-cli -u")
            exit(1)

    # Set timeout
    if 'TIMEOUT' in os.environ:
        tnglib.set_timeout(os.environ["TIMEOUT"])

    # Check if the SP is reachable
    if not tnglib.sp_health_check():
        print("Couldn't reach SP at \"" + tnglib.get_sp_path() + "\"")
        exit(1)

    # Check if token exists
    token = tnglib.get_token()

    if token[0]:
        if tnglib.is_token_valid():
           # pass token into headers
           tnglib.add_token_to_header(token[1])
        else:
            if args.subparser_name != 'login':
                print("Token is outdated. Obtain a new token through tng-cli login")
                exit(1)

    # login subcommand
    if args.subparser_name == 'login':
        # login needs exactly one argument
        if args.username:
            pswd = getpass.getpass('Password:')
            res, mes = tnglib.update_token(args.username, pswd, True)
            if not res:
                print(mes)
            exit(not res)
        else:
            msg = "Missing arguments for tng-cli login, " \
                  "-u/--username is required."
            print(msg)
            exit(1)


    # packages subcommand
    if args.subparser_name == 'package':
        # packages needs exactly one argument
        sel_args = [args.list, args.clean, args.upload, args.remove, args.get]
        arg_sum = len([x for x in sel_args if x])
        if arg_sum == 0:
            msg = "Missing arguments for tng-cli package. " \
                  "Type tng-cli package -h"
            print(msg)
            exit(1)

        if arg_sum > 1:
            msg = "Too many arguments for subcommand package. " \
                  "ype tng-cli package -h"
            print(msg)
            exit(1)

        if args.list:
            res, mes = tnglib.get_packages()
            order = ['package_uuid', 'name', 'version', 'created_at']
            form_print(mes, order)
            exit(not res)

        if args.upload:
            # Check if argument is a file
            if not args.upload.endswith('.tgo'):
                print("File or url does not point towards 5GTANTGO package.")
                exit(1)
            elif args.upload[:4] == 'http':
                res, mes = tnglib.upload_package(args.upload, url = True)
            elif not os.path.exists(args.upload):
                print("Input not a known file or url.")
                exit(1)
            else:
                res, mes = tnglib.upload_package(args.upload)
                print(mes)
                print(res)
                exit(not res)

        if args.remove:
            res, mes = tnglib.remove_package(args.remove)
            print(mes)
            exit(not res)

        if args.clean:
            res, mes = tnglib.remove_all_packages()
            for pkg in mes:
                print(pkg[1])
            exit(not res)

        if args.get:
            res, mes = tnglib.get_package(args.get)
            form_print(mes)
            exit(not res)

    # requests subcommand
    elif args.subparser_name == 'request':

        if bool(args.get):
            res, mes = tnglib.get_request(args.get)
            form_print(mes)
            exit(not res)
        else:
            res, mes = tnglib.get_requests()
            order = ['request_uuid',
                     'request_type',
                     'status',
                     'created_at',
                     'instance_uuid']
            form_print(mes, order)
            exit(not res)
    
    #monitor subcommand
    elif args.subparser_name == 'monitor':
        sel_args = [args.target_list, args.service_list, args.metric_list, args.vnf_uuid, args.vdu_uuid]
        arg_sum = len([x for x in sel_args if x])
        if arg_sum == 0:
            msg = "Missing arguments for tng-cli monitor. " \
                  "Type tng-cli monitor -h"
            print(msg)
            exit(1)

        if arg_sum > 3:
            msg = "Too many arguments for subcommand monitor. " \
                  "Type tng-cli monitor -h"
            print(msg)
            exit(1)

        if args.target_list:
            res, mes = tnglib.get_prometheus_targets()
            order = ['target', 'endpoint']
            form_print(mes, order)
            exit(not res)

        if args.service_list:
            res, mes = tnglib.get_services(args.service_list)
            order = ['vnf_uuid', 'vdu_uuid']
            form_print(mes, order)
            exit(not res)

        if args.metric_list:
            if not args.vnf_uuid:
                msg = "VNF uuid is missing " \
                      "Type tng-cli monitor -h"
                print(msg)
                exit(1)
            if not args.vdu_uuid:
                msg = "VDU uuid is missing " \
                      "Type tng-cli monitor -h"
                print(msg)
                exit(1)

            res, mes = tnglib.get_metrics(args.vnf_uuid, args.vdu_uuid)
            order = ['metric_name',]
            form_print(mes, order)
            exit(not res)
    
    # services subcommand
    elif args.subparser_name == 'service':
        # services needs exactly one argument
        sel_args = [args.descriptor,
                    args.instance,
                    args.instantiate,
                    args.terminate,
                    args.scale_out,
                    args.scale_in]
        arg_sum = len([x for x in sel_args if x])
        if arg_sum == 0:
            msg = "Missing arguments for subcommand service. " \
                  "Select either --descriptor, --instance, " \
                  "--instantiate or --terminate"
            print(msg)
            exit(1)

        if arg_sum > 1:
            msg = "To ao many rguments for subcommand service. " \
                  "Select either --descriptor, --instance, " \
                  "--instantiate or --terminate"
            print(msg)
            exit(1)

        sel_args = [args.instantiate, args.terminate, args.get]
        arg_sum = len([x for x in sel_args if x])
        if arg_sum == 2:
            print("--get can't be used with --instantiate or --terminate")
            exit(1)

        if args.descriptor and bool(args.get):
            res, mes = tnglib.get_service_descriptor(args.get)
            form_print(mes)
            exit(not res)

        if args.descriptor:
            res, mes = tnglib.get_service_descriptors()
            order = ['descriptor_uuid', 'name', 'version', 'created_at']
            form_print(mes, order)
            exit(not res)

        if args.instance and bool(args.get):
            res, mes = tnglib.get_service_instance(args.get)
            form_print(mes)
            exit(not res)

        if args.instance:
            res, mes = tnglib.get_service_instances()
            order = ['instance_uuid', 'name', 'status', 'created_at']
            form_print(mes, order)
            exit(not res)

        if bool(args.instantiate):
            if bool(args.sla):
                res, mes = tnglib.service_instantiate(args.instantiate,
                                                      args.sla)
            else:
                res, mes = tnglib.service_instantiate(args.instantiate)

            form_print(mes)
            exit(not res)

        if bool(args.terminate):
            res, mes = tnglib.service_terminate(args.terminate)
            form_print(mes)
            exit(not res)

        if bool(args.scale_out):
            if not bool(args.vnfd_uuid):
                print(" --vnfd_uuid is needed with --scale_out")
                exit(1)

            res, mes = tnglib.service_scale_out(args.scale_out,
                                                args.vnfd_uuid,
                                                args.num_instances,
                                                args.vim_uuid)
            form_print(mes)
            exit(not res)

        if bool(args.scale_in):
            if not (bool(args.vnfd_uuid) or bool(args.vnf_uuid)):
                msg = " --either --vnfd_uuid or --vnf_uuid is " \
                      "needed with --scale_in"
                print(msg)
                exit(1)

            res, mes = tnglib.service_scale_in(args.scale_in,
                                               args.vnf_uuid,
                                               args.vnfd_uuid,
                                               args.num_instances)
            form_print(mes)
            exit(not res)

    # functions subcommand
    elif args.subparser_name == 'function':
        # functions needs exactly one argument
        arg_sum = args.descriptor + args.instance
        if arg_sum == 0:
            msg = "Missing arguments for subcommand function. " \
                  "Select either --descriptor or --instance"
            print(msg)
            exit(1)

        if arg_sum > 1:
            msg = "Too many arguments for subcommand function. " \
                  "Select either --descriptor or --instance"
            print(msg)
            exit(1)

        if args.descriptor and bool(args.get):
            res, mes = tnglib.get_function_descriptor(args.get)
            form_print(mes)
            exit(not res)

        if args.descriptor:
            res, mes = tnglib.get_function_descriptors()
            order = ['descriptor_uuid', 'name', 'version', 'created_at']
            form_print(mes, order)
            exit(not res)

        if args.instance and bool(args.get):
            res, mes = tnglib.get_function_instance(args.get)
            form_print(mes)
            exit(not res)

        if args.instance:
            res, mes = tnglib.get_function_instances()
            order = ['instance_uuid', 'status', 'version', 'created_at']
            form_print(mes, order)
            exit(not res)

    # sla subcommand
    elif args.subparser_name == 'sla':
        # template, agreement or violation needs to be specified
        sel_args = [args.template,
                    args.agreement,
                    args.violation,
                    args.guarantee]
        arg_sum = len([x for x in sel_args if x])
        if arg_sum == 0:
            msg = "One of --template, --agreement, --violation, " \
                  " --guarantee must be specified with sla subcommand."
            print(msg)
            exit(1)

        elif arg_sum > 1:
            msg = "Only one of --template, --agreement, --violation, " \
                  " --guarantee must be specified with sla subcommand."
            print(msg)
            exit(1)

        if args.guarantee:
            res, mes = tnglib.get_sla_guarantees()
            order = ['name', 'id', 'operator', 'value']
            form_print(mes, order)
            exit(not res)

        elif args.template:
            # agreement and violation specific arguments are not allowed

            # If no argument is provided, list all templates
            sel_args = [args.create,
                        args.remove,
                        args.get,
                        args.nsd,
                        args.guarantee_id,
                        args.date
                        ]

            arg_sum = len([x for x in sel_args if x])
            if arg_sum == 0:
                res, mes = tnglib.get_sla_templates()
                order = ['sla_uuid', 'name', 'service', 'created_at']
                form_print(mes, order)
                exit(not res)

            arg_sum = bool(args.create) + bool(args.remove) + bool(args.get)
            # If one of --create, --remove or --get is provided,
            # perform the action
            if arg_sum == 1:
                if bool(args.get):
                    res, mes = tnglib.get_sla_template(args.get)
                    form_print(mes)
                    exit(not res)

                if bool(args.create):
                    if not (bool(args.nsd)):
                        msg = " --service is required " \
                              "with --template --create <NAME>"
                        print(msg)
                        exit(1)
                    else:
                        date = '01/01/2025'
                        if bool(args.date):
                            date = args.date
                        guarantee_id = None
                        if bool(args.guarantee_id):
                            guarantee_id = args.guarantee_id
                        sl_type = 'public'
                        if bool(args.sl_type):
                            sl_type = args.sl_type
                        as_instances = '100'
                        if bool(args.as_instances):
                            as_instances = args.as_instances
                        sl_date = '01/01/2025'
                        if bool(args.sl_date):
                            sl_date = args.sl_date
                        initiator = 'admin'
                        if bool(args.initiator):
                            initiator = args.initiator
                        provider = 'default'
                        if bool(args.provider):
                            provider = args.provider
                        flavor = None
                        if bool(args.flavor):
                            flavor = args.flavor

                        res, mes = tnglib.create_sla_template(args.create,
                                                              args.nsd,
                                                              date,
                                                              guarantee_id,
                                                              sl_type,
                                                              as_instances,
                                                              sl_date,
                                                              initiator,
                                                              provider,
                                                              flavor)
                        print(mes)
                        exit(not res)

                if bool(args.remove):
                    res, mes = tnglib.delete_sla_template(args.remove)
                    if res:
                        print(args.remove)
                    else:
                        print(mes)
                    exit(not res)

            # Error in any other case
            else:
                pass

        elif args.agreement:
            # template specific arguments are not allowed
            sel_args = [args.create,
                        args.remove,
                        args.get,
                        args.nsd,
                        args.guarantee_id,
                        args.date]
            arg_sum = len([x for x in sel_args if x])
            if arg_sum > 0:
                print("Only --nsi and --sla allowed with --agreement")
                exit(1)

            if bool(args.nsi) and bool(args.sla):
                res, mes = tnglib.get_detailed_agreement(args.sla, args.nsi)
                form_print(mes)
                exit(not res)

            elif bool(args.nsi):
                res, mes = tnglib.get_agreements(args.nsi)
                order = ['sla_uuid', 'nsi_uuid', 'sla_status']
                form_print(mes, order)
                exit(not res)

            elif bool(args.sla):
                print('--sla requires --nsi when used with --agreement')
                exit(1)

            else:
                res, mes = tnglib.get_agreements()
                order = ['sla_name',
                         'sla_uuid',
                         'nsi_uuid',
                         'ns_name',
                         'sla_status']
                form_print(mes, order)
                exit(not res)

        elif args.violation:
            # template specific arguments are not allowed
            sel_args = [args.create,
                        args.remove,
                        args.get,
                        args.nsd,
                        args.guarantee_id,
                        args.date]
            arg_sum = len([x for x in sel_args if x])
            if arg_sum > 0:
                print("Only --nsi and --sla allowed with --violation")
                exit(1)

            if bool(args.nsi) and bool(args.sla):
                res, mes = tnglib.get_violations_per_nsi_sla(args.sla,
                                                             args.nsi)
                form_print(mes)
                exit(not res)

            elif bool(args.nsi):
                res, mes = tnglib.get_violations(args.nsi)
                order = ['sla_uuid',
                         'nsi_uuid',
                         'violation_time',
                         'alert_state']
                form_print(mes, order)
                exit(not res)

            elif bool(args.sla):
                print('--sla requires --nsi when used with --violation')
                exit(1)

            else:
                res, mes = tnglib.get_violations()
                order = ['sla_uuid',
                         'nsi_uuid',
                         'violation_time',
                         'alert_state']
                form_print(mes, order)
                exit(not res)

    elif args.subparser_name == 'slice':
        # Only one of create, remove, instantiate,
        # terminate, templates, instances can be active
        sel_args = [args.create,
                    args.remove,
                    args.instantiate,
                    args.terminate,
                    args.template,
                    args.instance]
        arg_sum = len([x for x in sel_args if x])

        if arg_sum == 0:
            msg = "One of --create, --remove, --terminate, --instantiate, " \
                  "--template or --instance needed with slice subcommand."
            print(msg)
            exit(1)

        if arg_sum > 1:
            msg = "Only one of --create, --remove, --terminate, " \
                  "--instantiate, --template or --instance needed " \
                  "with slice subcommand."
            print(msg)
            exit(1)

        if args.name and not args.instantiate:
            print("--name can only be combined with --instantiate.")
            exit(1)

        if args.description and not args.instantiate:
            print("--description can only be combined with --instantiate.")
            exit(1)

        order = None
        if args.template and not args.get:
            res, mes = tnglib.get_slice_templates()
            order = ['slice_uuid', 'name', 'version', 'created_at']

        elif args.template and args.get:
            res, mes = tnglib.get_slice_template(args.get)

        elif args.instance and not args.get:
            res, mes = tnglib.get_slice_instances()
            order = ['instance_uuid', 'name', 'template_uuid', 'created_at']

        elif args.instance and args.get:
            res, mes = tnglib.get_slice_instance(args.get)

        elif args.remove:
            res, mes = tnglib.delete_slice_template(args.remove)

        elif args.create:
            res, mes = tnglib.create_slice_template(args.create)

        elif args.instantiate:
            res, mes = tnglib.slice_instantiate(args.instantiate,
                                                args.name,
                                                args.description)

        elif args.terminate:
            res, mes = tnglib.slice_terminate(args.terminate)

        form_print(mes, order)
        exit(not res)

    elif args.subparser_name == 'policy':
        # --service and --sla can only appear with --attach
        if (args.service or args.sla) and not args.attach:
            print("--service and --sla can only be combined with --attach")
            exit(1)

        # Only one of --get, --create, --remove or --attach can be selected
        sel_args = [args.get, args.create, args.remove, args.attach]
        arg_sum = len([x for x in sel_args if x])

        if arg_sum > 1:
            msg = "Only one of --get, --create, --remove or " \
                  "--attach can be selected"
            print(msg)
            exit(1)

        if arg_sum == 0:
            res, mes = tnglib.get_policies()
            order = ['policy_uuid', 'name', 'service', 'created_at']
            form_print(mes, order)
            exit(not res)

        if bool(args.get):
            res, mes = tnglib.get_policy(args.get)
            form_print(mes)
            exit(not res)

        if bool(args.remove):
            res, mes = tnglib.delete_policy(args.remove)
            form_print(mes)
            exit(not res)

        if bool(args.create):
            res, mes = tnglib.create_policy(args.create)
            form_print(mes)
            exit(not res)

        if bool(args.attach):
            if not (bool(args.service) and bool(args.sla)):
                print("--attach requires both --service and --sla.")
            else:
                res, mes = tnglib.attach_policy(args.attach,
                                                args.service,
                                                args.sla)
                form_print(mes)
                exit(not res)

    # results subcommand
    elif args.subparser_name == 'result':

        if bool(args.get):
            res, mes = tnglib.get_test_result(args.get)
            form_print(mes)
            exit(not res)
        else:
            res, mes = tnglib.get_test_results()
            order = ['uuid',
                     'instance_uuid',
                     'package_id',
                     'service_uuid',
                     'test_uuid',
                     #'test_instance_uuid',
                     'status',
                     'created_at']
            form_print(mes, order)
            exit(not res)

    # plans subcommand
    elif args.subparser_name == 'plan':

        if bool(args.get):
            res, mes = tnglib.get_test_plan(args.get)
            form_print(mes)
            exit(not res)
        else:
            res, mes = tnglib.get_test_plans()
            order = ['uuid',
                     'service_uuid',
                     'test_uuid',
                     'test_set_uuid',
                     'status',
                     'test_result_uuid']
            form_print(mes, order)
            exit(not res)

    # tests subcommand
    elif args.subparser_name == 'test':

        if bool(args.get):
            res, mes = tnglib.get_test_descriptor(args.get)
            form_print(mes)
            exit(not res)
        else:
            res, mes = tnglib.get_test_descriptors()
            order = ['uuid',
                     'name',
                     'vendor',
                     'version',
                     'platforms',
                     'status',
                     'updated_at']
            form_print(mes, order)
            exit(not res)

    elif args.subparser_name:
        print("Subcommand " + args.subparser_name + " not support yet")
        exit(0)

    return


def parse_args(args):
    """
    This method parses the arguments provided with the cli command
    """
    parser = argparse.ArgumentParser(description="5GTANGO tng-cli tool")

    parser.add_argument('-u',
                        '--url',
                        dest='sp_url',
                        metavar="URL",
                        default=None,
                        help='Specify the service platform url')

    parser.add_argument('-v',
                        '--verbose',
                        dest='verbose',
                        action="store_true",
                        default=False,
                        help='Verbose output')

    subparsers = parser.add_subparsers(description='',
                                       dest='subparser_name')

    parser_pkg = subparsers.add_parser('package',
                                       help='actions related to packages')
    parser_ser = subparsers.add_parser('service',
                                       help='actions related to services')
    parser_req = subparsers.add_parser('request',
                                       help='actions related to requests')
    parser_fun = subparsers.add_parser('function',
                                       help='actions related to functions')
    parser_sla = subparsers.add_parser('sla',
                                       help='actions related to slas')
    parser_slc = subparsers.add_parser('slice',
                                       help='actions related to slices')
    parser_pol = subparsers.add_parser('policy',
                                       help='actions related to policies')
    parser_tests = subparsers.add_parser('test',
                                         help='actions related to test descriptors')
    parser_plans = subparsers.add_parser('plan',
                                         help='actions related to test-plans')
    parser_results = subparsers.add_parser('result',
                                         help='actions related to results')
    parser_mon = subparsers.add_parser('monitor',
                                         help='actions related to monitoring')
    parser_login = subparsers.add_parser('login',
                                         help='actions related to login')

    # login sub arguments
    parser_login.add_argument('-u',
                              '--username',
                              required=True,
                              metavar="USERNAME",
                              help='provide username')

    # packages sub arguments
    parser_pkg.add_argument('-l',
                            '--list',
                            action='store_true',
                            required=False,
                            default=False,
                            help='list the available packages')

    parser_pkg.add_argument('-r',
                            '--remove',
                            required=False,
                            default=False,
                            metavar='PACKAGE_UUID',
                            help='remove the specified package')

    parser_pkg.add_argument('-c',
                            '--clean',
                            action='store_true',
                            required=False,
                            default=False,
                            help='remove all packages')

    parser_pkg.add_argument('-u',
                            '--upload',
                            required=False,
                            default=False,
                            metavar='PACKAGE',
                            help='upload the package, from file or url')

    parser_pkg.add_argument('-g',
                            '--get',
                            metavar='PACKAGE_UUID',
                            required=False,
                            default=False,
                            help='get detailed info on a package')

    # requests sub arguments
    parser_req.add_argument('-g',
                            '--get',
                            metavar='UUID',
                            required=False,
                            default=False,
                            help='Returns detailed info on specified request')

    # services sub arguments
    parser_ser.add_argument('--descriptor',
                            action='store_true',
                            required=False,
                            default=False,
                            help='List all available service descriptors')

    parser_ser.add_argument('--instance',
                            action='store_true',
                            required=False,
                            default=False,
                            help='List all available service instances')

    help_mes = 'with --descriptor or --instace. Returns specified ' \
               'info on descriptor or instance'
    parser_ser.add_argument('-g',
                            '--get',
                            metavar='UUID',
                            required=False,
                            default=False,
                            help=help_mes)

    parser_ser.add_argument('-i',
                            '--instantiate',
                            metavar='SERVICE UUID',
                            required=False,
                            default=False,
                            help='Intantiate a service')

    parser_ser.add_argument('-t',
                            '--terminate',
                            metavar='INSTANCE UUID',
                            required=False,
                            default=False,
                            help='Terminate a service')

    help_mes = 'Only with --instantiate. Attach an SLA to instantiated service'
    parser_ser.add_argument('-s',
                            '--sla',
                            metavar='SLA UUID',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'Scale in a service, requires either --vnf_uuid or --vnfd_uuid'
    parser_ser.add_argument('--scale_in',
                            metavar='INSTANCE UUID',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'Scale out a service, requires --vnfd_uuid'
    parser_ser.add_argument('--scale_out',
                            metavar='INSTANCE UUID',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'Specify the vnf descriptor uuid, used with --scale_out '\
               ' and --scale_in'
    parser_ser.add_argument('--vnfd_uuid',
                            metavar='VNFD UUID',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'Specify the vnf instance uuid, used wit --scale_in'
    parser_ser.add_argument('--vnf_uuid',
                            metavar='VNF UUID',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'Number of instances to add/remove when scaling'
    parser_ser.add_argument('--num_instances',
                            metavar='NUMBER OF INSTANCES',
                            required=False,
                            default=False,
                            help=help_mes)

    parser_ser.add_argument('--vim_uuid',
                            metavar='VIM UUID',
                            required=False,
                            default=False,
                            help='Specify VIM uuid, only with --vnfd_uuid')

    # functions sub arguments
    parser_fun.add_argument('--descriptor',
                            action='store_true',
                            required=False,
                            default=False,
                            help='List all available function descriptors')

    parser_fun.add_argument('--instance',
                            action='store_true',
                            required=False,
                            default=False,
                            help='List all available function instances')

    help_mes = 'with --descriptor or --instace. Returns specified ' \
               'info on descriptor or instance'
    parser_fun.add_argument('-g',
                            '--get',
                            metavar='UUID',
                            required=False,
                            default=False,
                            help=help_mes)

    # sla sub arguments
    help_mes = 'Specify an action related to SLA templates. If no extra ' \
               'argument, returns all SLA templates.'
    parser_sla.add_argument('--template',
                            action='store_true',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'Specify an action related to SLA agreements. If no extra ' \
               'argument, returns all SLA agreements.'
    parser_sla.add_argument('--agreement',
                            action='store_true',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'Specify an action related to SLA violations. If no extra ' \
               'argument, returns all SLA violations.'
    parser_sla.add_argument('--violation',
                            action='store_true',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'List the available SLA guarantees. Does not require ' \
               'additional arguments.'
    parser_sla.add_argument('--guarantee',
                            action='store_true',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'Only with --template --create. Specify the experation date'
    parser_sla.add_argument('-d',
                            '--date',
                            metavar='DD/MM/YYYY',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'Only with --template --create. Specify the service uuid'
    parser_sla.add_argument('-s',
                            '--nsd',
                            metavar='SERVICE UUID',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'Only with --template --create. Specify the guarantee id'
    parser_sla.add_argument('-i',
                            '--guarantee-id',
                            metavar='GUARANTEE ID',
                            default=False,
                            help=help_mes)

    help_mes = 'Only with --template --create. Specify the license type'
    parser_sla.add_argument('-slt',
                            '--sl-type',
                            metavar='LICENSE TYPE',
                            default=False,
                            help=help_mes)

    help_mes = 'Only with --template --create. Specify the allowed number of instances'
    parser_sla.add_argument('-asi',
                            '--as-instances',
                            metavar='ALLOWED INSTANCES',
                            default=False,
                            help=help_mes)

    help_mes = 'Only with --template --create. Specify the license exp date'
    parser_sla.add_argument('-sld',
                            '--sl-date',
                            metavar='LICENSE EXP DATE',
                            default=False,
                            help=help_mes)

    help_mes = 'Only with --template --create. Specify the template initiator'
    parser_sla.add_argument('-in',
                            '--initiator',
                            metavar='INITIATOR NAME',
                            default=False,
                            help=help_mes)

    help_mes = 'Only with --template --create. Specify the the template provider'
    parser_sla.add_argument('-pr',
                            '--provider',
                            metavar='PROVIDER NAME',
                            default=False,
                            help=help_mes)

    help_mes = 'Only with --template --create. Specify the flavor name'
    parser_sla.add_argument('-fl',
                            '--flavor',
                            metavar='FLAVOR NAME',
                            default=False,
                            help=help_mes)

    help_mes = 'Only with --template. Create a new SLA template. ' \
               'Requires -s and -i'
    parser_sla.add_argument('-c',
                            '--create',
                            metavar='SLA NAME',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'Only with --template. Remove an SLA template.'
    parser_sla.add_argument('-r',
                            '--remove',
                            metavar='SLA TEMPLATE UUID',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'With --template, --agreement and --violation. Get ' \
               'descriptor associated to uuid.'
    parser_sla.add_argument('-g',
                            '--get',
                            metavar='UUID',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'Only with --agreement or --violation. Specify ' \
               'the service instance uuid'
    parser_sla.add_argument('-n',
                            '--nsi',
                            metavar='SERVICE INSTANCE UUID',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'Only with --agreement -n or --violation -n. ' \
               'Specify the sla uuid'
    parser_sla.add_argument('-t',
                            '--sla',
                            metavar='SERVICE INSTANCE UUID',
                            required=False,
                            default=False,
                            help=help_mes)

    # slice related arguments
    parser_slc.add_argument('--template',
                            action='store_true',
                            required=False,
                            default=False,
                            help='List the available slice templates')

    parser_slc.add_argument('--instance',
                            action='store_true',
                            required=False,
                            default=False,
                            help='List the available slice instances')

    help_mes = 'Use with --template or --instance. Returns single ' \
               'template or instance'
    parser_slc.add_argument('-g',
                            '--get',
                            metavar='UUID',
                            required=False,
                            default=False,
                            help=help_mes)

    parser_slc.add_argument('-r',
                            '--remove',
                            metavar='TEMPLATE UUID',
                            required=False,
                            default=False,
                            help='Remove slice template')

    parser_slc.add_argument('-t',
                            '--terminate',
                            metavar='INSTANCE UUID',
                            required=False,
                            default=False,
                            help='Terminate slice instance')

    parser_slc.add_argument('-c',
                            '--create',
                            metavar='SLICE TEMPLATE',
                            required=False,
                            default=False,
                            help='Create a new slice template from file')

    parser_slc.add_argument('-i',
                            '--instantiate',
                            metavar='TEMPLATE UUID',
                            required=False,
                            default=False,
                            help='Instantiate a new slice instance')

    help_mes = 'Only with --instantiate. Define the name for the ' \
               'slice instance.'
    parser_slc.add_argument('-n',
                            '--name',
                            metavar='SLICE INSTANCE NAME',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'Only with --instantiate. Define the description for the ' \
               'slice instance.'
    parser_slc.add_argument('-d',
                            '--description',
                            metavar='SLICE INSTANCE NAME',
                            required=False,
                            default=False,
                            help=help_mes)

    # Policy subcommands
    parser_pol.add_argument('-g',
                            '--get',
                            metavar='POLICY UUID',
                            required=False,
                            default=False,
                            help='Get detailed policy information')

    parser_pol.add_argument('-c',
                            '--create',
                            metavar='POLICY FILE',
                            required=False,
                            default=False,
                            help='Create a new policy from json or yaml file')

    parser_pol.add_argument('-r',
                            '--remove',
                            metavar='POLICY UUID',
                            required=False,
                            default=False,
                            help='Remove a policy descriptor')

    help_mes = 'Requires --service and --sla. Attach policy ' \
               'to a service and sla'
    parser_pol.add_argument('-a',
                            '--attach',
                            metavar='POLICY UUID',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'Only with --attach. Attach policy to a service'
    parser_pol.add_argument('-n',
                            '--service',
                            metavar='SERVICE UUID',
                            required=False,
                            default=False,
                            help=help_mes)

    parser_pol.add_argument('-s',
                            '--sla',
                            metavar='SLA UUID',
                            required=False,
                            default=False,
                            help='Only with --attach. Attach policy to an sla')
    # monitoring sub arguments
    help_mes = 'Get list of monitoring endpoints'
    parser_mon.add_argument('-trl',
                            '--target-list',
                            action='store_true',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'Get active monitoring services'
    parser_mon.add_argument('-srv',
                            '--service-list',
                            metavar='SERVICE UUID',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'Only with --metric-list. Get metric list per vnf/vdu'
    parser_mon.add_argument('-vnf',
                            '--vnf-uuid',
                            metavar='FUNCTION UUID',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'Only with --metric-list. Get metric list per vnf/vdu'
    parser_mon.add_argument('-vdu',
                            '--vdu-uuid',
                            metavar='VDU UUID',
                            required=False,
                            default=False,
                            help=help_mes)

    help_mes = 'Get metrics list'
    parser_mon.add_argument('-mtr',
                            '--metric-list',
                            action='store_true',
                            required=False,
                            default=False,
                            help=help_mes)
    # tests sub arguments
    parser_tests.add_argument('-g',
                              '--get',
                              metavar='UUID',
                              required=False,
                              default=False,
                              help='Returns detailed info on specified test descriptor')

    parser_plans.add_argument('-g',
                              '--get',
                              metavar='UUID',
                              required=False,
                              default=False,
                              help='Returns detailed info on specified test-plan')

    parser_results.add_argument('-g',
                          '--get',
                          metavar='UUID',
                          required=False,
                          default=False,
                          help='Returns detailed info on specified test-plan')

    return parser.parse_args(args)


def form_print(data, order=None):
    """
    Formatted printing
    """
    if isinstance(data, list):
        if order is None:
            if bool(data):
                order = data[0].keys()
            else:
                return

        # print header
        header = ''
        for key in order:
            if ('uuid' in key) or ('metric' in key):
                new_seg = key.replace('_', ' ').upper().ljust(40)
            # elif key == 'version':
            #     new_seg = key.upper().ljust(10)
            else:
                new_seg = key.replace('_', ' ').upper().ljust(20)
            header = header + new_seg
        print(header)

        # print content
        for data_seg in data:
            line = ''
            for key in order:
                if ('uuid' in key) or ('metric' in key):
                    new_seg = data_seg[key].ljust(40)
                elif key in ['created_at', 'updated_at', 'violation_time']:
                    new_seg = data_seg[key][:16].replace('T', ' ').ljust(20)
                else:
                    new_seg = data_seg[key][:18].ljust(20)
                line = line + new_seg
            print(line)

    elif isinstance(data, dict):
        print('')
        print(yaml.dump(data, default_flow_style=False))

    else:
        print(data)

    return


def init_logger(verbose):
    """
    Configure logging
    """
    if verbose:
        level = logging.DEBUG
        logging.getLogger("tnglib").setLevel(level)
        logging.getLogger(__name__).setLevel(level)
        logging.basicConfig(level=level)

    return
