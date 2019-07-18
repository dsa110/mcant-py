#!/usr/bin/env python3
"""mcant is an etcd client for control and monitor of DSA110 antennas
"""

import argparse
import json
from time import sleep
import yaml
import etcd3

DBG = True


def read_yaml(fname):
    """Read a YAML formatted file.

    :param fn: YAML formatted filename"
    :type fn: String
    :return: Dictionary on success. None on error
    :rtype: Dictionary
    """

    with open(fname, 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            return None


def dprint(msg, level, dbg=True):
    """Simple print which can be turned off.

    :param msg: String to print.
    :param level: String preceeding msg(typically INFO, WARN etc)
    :param dbg: Boolean to print or not.
    :type msg: String
    :type level: String
    :type dbg: Boolean
    """

    if dbg:
        print("{}: {}".format(level, msg))


def parse_endpoint(endpoint):
    """Parse the endpoint string in the first element of the list.
       Go allows multiple endpoints to be specified
       whereas Python only one and has separate args for host and port.

    :param endpoint: host port string of the form host:port.
    :type endpoint: List
    :return: Tuple (host, port)
    :rtype: Tuple
    """

    host, port = endpoint[0].split(':')
    return host, port


def parse_value(value):
    """Parse the string in JSON format and assumed represent a dictionary.

    :param value: JSON string of the form: {"key":"value"}
                  or {"key":number|bool}
    :type value: String
    :return: Key,value dictionary
    :rtype: Dictionary
    """

    rtn = {}
    try:
        rtn = json.loads(value)
    except ValueError:
        dprint("parse_value(): JSON Decode Error. Check JSON. value= {}".
               format(value), 'ERR')
    return rtn


def process_command(event):
    """Etcd watch callback function. Called when values of watched
       keys are updated.

    :param event: Etcd event containing the key and value.
    :type event: TODO fill in.
    """

    dprint("process_command() event= {}".format(event), 'INFO', DBG)
    key = event.key.decode('utf-8')
    value = event.value.decode('utf-8')
    dprint("key= {}, value= {}".format(key, value), 'INFO', DBG)
    # parse the JSON command
    cmd = parse_value(value)
    for key, val in cmd.items():
        dprint("cmd key= {}, cmd val= {}".format(key, val), 'INFO', DBG)


def backend_run(args):
    """Main entry point. Will never return.

    :param args: Input arguments from argparse.
    """

    dprint(args.etcd_file, 'INFO', DBG)
    etcd_params = read_yaml(args.etcd_file)
    etcd_host, etcd_port = parse_endpoint(etcd_params['endpoints'])
    dprint("etcd host={}, etcd port={}".format(etcd_host, etcd_port), 'INFO')
    etcd = etcd3.client(host=etcd_host, port=etcd_port)
    watch_ids = []
    for cmd in etcd_params['commands']:
        watch_id = etcd.add_watch_callback(cmd, process_command)
        watch_ids.append(watch_id)

    while True:
        sleep(5)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-ef', '--etcd_file', type=str,
                        default='etcdConfig.yml',
                        help='etcd parameters')
    the_args = parser.parse_args()
    dprint(the_args, 'INFO', DBG)
    backend_run(the_args)
