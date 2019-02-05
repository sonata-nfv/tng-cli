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
            print("Provide path to service platform through SP_PATH or tng-cli -u")
            exit(1)

    # Check if the SP is reachable
    if not tnglib.sp_health_check():
        print("Couldn't reach SP at \"" + tnglib.get_sp_path() + "\"")
        exit(1)

    # packages subcommand
    if args.subparser_name=='package':
        # packages needs exactly one argument     
        arg_sum = args.list + args.clean + bool(args.upload) + bool(args.remove) + bool(args.get)
        if arg_sum == 0:
            print("Missing arguments for subcommand package. Type tng-cli package -h")
            exit(1)

        if arg_sum > 1:
            print("Too many arguments for subcommand package. Type tng-cli package -h")
            exit(1)

        if args.list:
            res, mes = tnglib.get_packages()
            order = ['package_uuid', 'name', 'version', 'created_at']
            form_print(mes, order)
            exit(not res)

        if args.upload:
            # Check if argument is a file
            if not os.path.exists(args.upload):
                print("No known package with that name.")
                exit(1)
            elif not args.upload.endswith('.tgo'):
                print("File is not a 5GTANTGO package.")
                exit(1)
            else:
                res, mes = tnglib.upload_package(args.upload)
                print(mes)
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

    # services subcommand
    elif args.subparser_name=='service':
        # services needs exactly one argument     
        arg_sum = args.list + bool(args.get)
        if arg_sum == 0:
            print("Missing arguments for subcommand service. Type tng-cli service -h")
            exit(1)

        if arg_sum > 1:
            print("Too many arguments for subcommand service. Type tng-cli service -h")
            exit(1)

        if args.list:
            res, mes = tnglib.get_services()
            order = ['service_uuid', 'name', 'version', 'created_at']
            form_print(mes, order)
            exit(not res)

        if args.get:
            res, mes = tnglib.get_service(args.get)
            form_print(mes)
            exit(not res)

    # functions subcommand
    elif args.subparser_name=='function':
        # functions needs exactly one argument     
        arg_sum = args.list + bool(args.get)
        if arg_sum == 0:
            print("Missing arguments for subcommand function. Type tng-cli service -h")
            exit(1)

        if arg_sum > 1:
            print("Too many arguments for subcommand function. Type tng-cli service -h")
            exit(1)

        if args.list:
            res, mes = tnglib.get_functions()
            order = ['function_uuid', 'name', 'version', 'created_at']
            form_print(mes, order)
            exit(not res)

        if args.get:
            res, mes = tnglib.get_function(args.get)
            form_print(mes)
            exit(not res)

    # sla subcommand
    elif args.subparser_name=='sla':
        # template, agreement or violation needs to be specified
        arg_sum = args.template + args.agreement + args.violation + args.guarantee
        if arg_sum == 0:
            print("One of --template, --agreement, --violation, --guarantee must be specified with sla subcommand.")
            exit(1)

        elif arg_sum > 1:
            print("Only one of --template, --agreement, --violation, --guarantee can be specified with sla subcommand.")
            exit(1)

        if args.guarantee:
            res, mes = tnglib.get_sla_guarantees()
            order = ['name', 'id', 'operator', 'value']
            form_print(mes, order)
            exit(not res)

        elif args.template:
            # agreement and violation specific arguments are not allowed

            # If no argument is provided, list all templates
            arg_sum = bool(args.create) + bool(args.remove) + bool(args.get) + bool(args.nsd) + bool(args.guarantee_id) + bool(args.date)
            if arg_sum == 0:
                res, mes = tnglib.get_sla_templates()
                order = ['sla_uuid', 'name', 'created_at']
                form_print(mes, order)
                exit(not res)

            arg_sum = bool(args.create) + bool(args.remove) + bool(args.get)
            # If one of --create, --remove or --get is provided, perform the action
            if arg_sum == 1:
                if bool(args.get):
                    res, mes = tnglib.get_sla_template(args.get)
                    form_print(mes)
                    exit (not res)

                if bool(args.create):
                    if not (bool(args.nsd) and bool(args.guarantee_id)):
                        print("Both --service and --guarantee are required with --template --create <NAME>")
                        exit(1)
                    else:
                        date = '01/01/2025'
                        if bool(args.date):
                            date = args.date
                        res, mes = tnglib.create_sla_template(args.create, args.nsd, date, args.guarantee_id)
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
            arg_sum = bool(args.create) + bool(args.remove) + bool(args.get) + bool(args.nsd) + bool(args.guarantee_id) + bool(args.date)
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
                order = ['sla_name', 'sla_uuid', 'nsi_uuid', 'ns_name', 'sla_status']
                form_print(mes, order)
                exit(not res)

        elif args.violation:
            # template specific arguments are not allowed
            arg_sum = bool(args.create) + bool(args.remove) + bool(args.get) + bool(args.nsd) + bool(args.guarantee_id) + bool(args.date)
            if arg_sum > 0:
                print("Only --nsi and --sla allowed with --violation")
                exit(1)

            if bool(args.nsi) and bool(args.sla):
                res, mes = tnglib.get_violations_per_nsi_sla(args.sla, args.nsi)
                form_print(mes)
                exit(not res)

            elif bool(args.nsi):
                res, mes = tnglib.get_violations(args.nsi)
                order = ['sla_uuid', 'nsi_uuid', 'violation_time', 'alert_state']
                form_print(mes, order)
                exit(not res)

            elif bool(args.sla):
                print('--sla requires --nsi when used with --violation')
                exit(1)

            else:
                res, mes = tnglib.get_violations()
                order = ['sla_uuid', 'nsi_uuid', 'violation_time', 'alert_state']
                form_print(mes, order)
                exit(not res)

    elif args.subparser_name == 'slice':
        # Only one of create, remove, instantiate, terminate, templates, instances can be active
        arg_sum = bool(args.create) + bool(args.remove) + bool(args.instantiate) + bool(args.terminate) + bool(args.templates) + bool(args.instances)

        if arg_sum == 0:
            print("One of --create, --remove, --terminate, --instantiate, --templates or --instances needed with slice subcommand.")
            exit(1)

        if arg_sum > 1:
            print("Only one of --create, --remove, --terminate, --instantiate, --templates or --instances allowed with slice subcommand.")
            exit(1)

        if bool(args.templates) and not bool(args.get):
            res, mes = tnglib.get_slice_templates()
            order = ['slice_uuid', 'name', 'version', 'created_at']
            form_print(mes, order)
            exit(not res)
            
        if bool(args.templates) and bool(args.get):
            res, mes = tnglib.get_slice_template(args.get)
            form_print(mes)
            exit(not res)

        if bool(args.instances) and not bool(args.get):
            res, mes = tnglib.get_slice_instances()
            order = ['instance_uuid', 'name', 'template_uuid', 'created_at']
            form_print(mes, order)
            exit(not res)
            
        if bool(args.instances) and bool(args.get):
            res, mes = tnglib.get_slice_instance(args.get)
            form_print(mes)
            exit(not res)

        if bool(args.remove):
            res, mes = tnglib.delete_slice_template(args.remove)
            form_print(mes)
            exit(not res)

        if bool(args.create):
            res, mes = tnglib.create_slice_template(args.create)
            form_print(mes)
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

    subparsers = parser.add_subparsers(description='<submodule> -h for more info',
                                       dest='subparser_name')

    parser_pkg = subparsers.add_parser('package', help='actions related to packages')
    parser_ser = subparsers.add_parser('service', help='actions related to services')
    parser_req = subparsers.add_parser('request', help='actions related to requests')
    parser_fun = subparsers.add_parser('function', help='actions related to functions')
    parser_sla = subparsers.add_parser('sla', help='actions related to slas')
    parser_slc = subparsers.add_parser('slice', help='actions related to slices')

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
                            help='upload the specified package')

    parser_pkg.add_argument('-g',
                            '--get', 
                            metavar='PACKAGE_UUID',
                            required=False,
                            default=False,
                            help='get detailed info on a package')


    # services sub arguments
    parser_ser.add_argument('-l',
                            '--list', 
                            action='store_true',
                            required=False,
                            default=False,
                            help='list the available services')

    parser_ser.add_argument('-g',
                            '--get', 
                            metavar='SERVICE_UUID',
                            required=False,
                            default=False,
                            help='get detailed info on a service')

    # functions sub arguments
    parser_fun.add_argument('-l',
                            '--list', 
                            action='store_true',
                            required=False,
                            default=False,
                            help='list the available functions')

    parser_fun.add_argument('-g',
                            '--get', 
                            metavar='FUNCTION_UUID',
                            required=False,
                            default=False,
                            help='get detailed info on a function')


    # sla sub arguments
    parser_sla.add_argument('--template', 
                            action='store_true',
                            required=False,
                            default=False,
                            help='Specify an action related to SLA templates. If no extra argument, returns all SLA templates.')

    parser_sla.add_argument('--agreement', 
                            action='store_true',
                            required=False,
                            default=False,
                            help='Specify an action related to SLA agreements. If no extra argument, returns all SLA agreements.')

    parser_sla.add_argument('--violation', 
                            action='store_true',
                            required=False,
                            default=False,
                            help='Specify an action related to SLA violations. If no extra argument, returns all SLA violations.')

    parser_sla.add_argument('--guarantee', 
                            action='store_true',
                            required=False,
                            default=False,
                            help='List the available SLA guarantees. Does not require additional arguments.')

    parser_sla.add_argument('-d',
                            '--date', 
                            metavar='DD/MM/YYYY',
                            required=False,
                            default=False,
                            help='Only with --template --create. Specify the experation date')

    parser_sla.add_argument('-s',
                            '--nsd', 
                            metavar='SERVICE UUID',
                            required=False,
                            default=False,
                            help='Only with --template --create. Specify the service uuid')

    parser_sla.add_argument('-i',
                            '--guarantee-id', 
                            metavar='GUARANTEE ID',
                            required=False,
                            default=False,
                            help='Only with --template --create. Specify the guarantee id')

    parser_sla.add_argument('-c',
                            '--create', 
                            metavar='SLA NAME',
                            required=False,
                            default=False,
                            help='Only with --template. Create a new SLA template. Requires -s and -i')

    parser_sla.add_argument('-r',
                            '--remove', 
                            metavar='SLA TEMPLATE UUID',
                            required=False,
                            default=False,
                            help='Only with --template. Remove an SLA template.')

    parser_sla.add_argument('-g',
                            '--get', 
                            metavar='UUID',
                            required=False,
                            default=False,
                            help='With --template, --agreement and --violation. Get descriptor associated to uuid.')

    parser_sla.add_argument('-n',
                            '--nsi', 
                            metavar='SERVICE INSTANCE UUID',
                            required=False,
                            default=False,
                            help='Only with --agreement or --violation. Specify the service instance uuid')

    parser_sla.add_argument('-t',
                            '--sla', 
                            metavar='SERVICE INSTANCE UUID',
                            required=False,
                            default=False,
                            help='Only with --agreement -n or --violation -n. Specify the sla uuid')

    # slice related arguments
    parser_slc.add_argument('--templates', 
                            action='store_true',
                            required=False,
                            default=False,
                            help='List the available slice templates')

    parser_slc.add_argument('--instances', 
                            action='store_true',
                            required=False,
                            default=False,
                            help='List the available slice instances')

    parser_slc.add_argument('-g',
                            '--get', 
                            metavar='UUID',
                            required=False,
                            default=False,
                            help='Use with --templates or --instances. Returns single template or instance')

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
            if 'uuid' in key:
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
                if 'uuid' in key:
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
