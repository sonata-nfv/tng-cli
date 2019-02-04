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
    if args.subparser_name=='packages':
        # packages needs exactly one argument     
        arg_sum = args.list + args.clean + bool(args.upload) + bool(args.remove) + bool(args.get)
        if arg_sum == 0:
            print("Missing arguments for subcommand packages. Type tng-cli packages -h")
            exit(1)

        if arg_sum > 1:
            print("Too many arguments for subcommand packages. Type tng-cli packages -h")
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
    elif args.subparser_name=='services':
        # services needs exactly one argument     
        arg_sum = args.list + bool(args.get)
        if arg_sum == 0:
            print("Missing arguments for subcommand services. Type tng-cli services -h")
            exit(1)

        if arg_sum > 1:
            print("Too many arguments for subcommand services. Type tng-cli services -h")
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
    elif args.subparser_name=='functions':
        # functions needs exactly one argument     
        arg_sum = args.list + bool(args.get)
        if arg_sum == 0:
            print("Missing arguments for subcommand functions. Type tng-cli services -h")
            exit(1)

        if arg_sum > 1:
            print("Too many arguments for subcommand functions. Type tng-cli services -h")
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

    parser_pkg = subparsers.add_parser('packages', help='actions related to packages, packages --help')
    parser_ser = subparsers.add_parser('services', help='actions related to services, services --help')
    parser_req = subparsers.add_parser('requests', help='actions related to requests, requests --help')
    parser_fun = subparsers.add_parser('functions', help='actions related to functions, functions --help')

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
                elif key in ['created_at', 'updated_at']:
                    new_seg = data_seg[key][:16].replace('T', ' ')
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
