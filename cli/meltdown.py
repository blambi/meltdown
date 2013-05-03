#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import urllib2
import argparse
import os
import ConfigParser
import httplib2

__author__ = "Patrik Lembke <blambi@chebab.com>"
__version__ = "0.1"

class REST_Kernel:
    def __init__(self, base_uri):
        self.base_uri = base_uri
        self.user_agent = "MeltdownPY {0}".format(__version__)

    def __post(self, body, uri = None):
        body = json.dumps(body)

        if uri:
            full_uri = self.base_uri + uri
        else:
            full_uri = self.base_uri
        request = urllib2.Request(full_uri, body,
                                  {'Content-Type': 'application/json',
                                   'User-Agent': self.user_agent})
        try:
            fp = urllib2.urlopen((request))
        except urllib2.HTTPError, why:
            return { 'error': why }

        response = fp.read()
        return json.loads(response)

    def __put(self, body = None, uri = None):
        if body:
            body = json.dumps(body)

        if uri:
            full_uri = self.base_uri + uri
        else:
            full_uri = self.base_uri

        http = httplib2.Http()
        response, content = http.request(full_uri, 'PUT', body=body, headers =
                                         {'Content-Type': 'application/json',
                                          'User-Agent': self.user_agent})

        if response['content-type'] == 'application/json':
            return json.loads(content)

        return {'success': False, 'why': "Unknown data returned with status {0}".format(response['status'])}

    def __get(self, uri = None):
        if uri:
            full_uri = self.base_uri + uri
        else:
            full_uri = self.base_uri
        request = urllib2.Request(full_uri, None,
                                  {'Content-Type': 'application/json',
                                   'User-Agent': self.user_agent})
        try:
            fp = urllib2.urlopen((request))
        except urllib2.HTTPError, why:
            return { 'error': why }

        response = fp.read()
        return json.loads(response)

    def get_all_open(self):
        response = self.__get()
        return response

    def new_issue(self, who, what):
        """Tries to report a new issue to the server"""
        body = {'who': who, 'what': what}

        try:
            response = self.__post(body)
        except ValueError, why:
            return { 'error': True, 'why': why }

        if response.has_key('success'):
            if response['success']:
                return { 'error': False, 'id': response['id'] }
            else:
                return { 'error': True, 'why': response['why'] }
        return False

    def close_issue(self, id):
        """Tries to close an issue"""

        try:
            response = self.__put(body = None, uri = "/{0}/close".format(id))
        except ValueError, why:
            return {'error': True, 'why': why}

        if response.has_key('success'):
            if response['success']:
                return { 'error': False, 'id': response['id'] }
            else:
                return { 'error': True, 'why': response['why'] }
        return False

    def update_issue(self, id, updates):
        try:
            response = self.__put(body = updates, uri = "/{0}".format(id))
        except ValueError, why:
            return {'error': True, 'why': why}

        if response.has_key('success'):
            if response['success']:
                return { 'error': False, 'id': response['id'], 'issue': response['issue'] }
            else:
                return { 'error': True, 'why': response['why'] }
        return False


class ConfigManager:
    defaults = {
        'who': None,
        'uri': "http://localhost:80"}

    def __init__(self, conf_file=None):
        if conf_file:
            self.conf_file = conf_file
        elif os.path.exists('{0}/.meltdown.conf'.format(os.path.expanduser('~'))):
            self.conf_file = '{0}/.meltdown.conf'.format(os.path.expanduser('~'))
        elif os.path.exists('/etc/meltdown.conf'):
            self.conf_file = '/etc/meltdown.conf'
        else:
            self.conf_file = None

        self.conf = ConfigParser.ConfigParser(self.defaults)

        if self.conf_file:
            self.conf.read(self.conf_file)

    def get(self, key):
        return self.conf.get('meltdown', key)


# Commands
def cmd_report(args):
    ret = kernel.new_issue(args.who, args.WHAT)

    if ret and ret['error']:
        print("ERR: {0}.".format(ret['why']))
    elif ret:
        print("OK: Created issue #{0}.".format(ret['id']))
    else:
        print("ERR: Undefined error occurred.")

def cmd_list(args):
    open_issues = kernel.get_all_open()

    print("ID\tWho\tWhat")
    for issue in open_issues:
        print("{0}\t{1}\t{2}".format(issue['id'],
                                     issue['who'].encode('utf-8'),
                                     issue['what'].encode('utf-8')))

def cmd_close(args):
    ret = kernel.close_issue(args.ID)

    if ret and ret['error']:
        print("ERR: {0}.".format(ret['why']))
    elif ret:
        print("OK: Closed issue #{0}.".format(ret['id']))
    else:
        print("ERR: Undefined error occurred.")

def cmd_steal(args):
    ret = kernel.update_issue(args.ID, {'who': args.who})

    if ret and ret['error']:
        print("ERR: {0}.".format(ret['why']))
    elif ret:
        print("OK: Stole issue #{0}.".format(ret['id']))
    else:
        print("ERR: Undefined error occurred.")


# -- main
if __name__ == '__main__':
    # Settings
    config = ConfigManager()

    # This needs some work, but basic arg parsing is ready
    arg_parser = argparse.ArgumentParser(description = "Meltdown client - Report whats up etc.")
    arg_parser.add_argument('-u', '--uri', type=str,
                            help="URI to connect to (default http://localhost:80).",
                            default=config.get('uri'))

    # Subcommands
    subparsers = arg_parser.add_subparsers(help='sub-command help')

    # report
    parser_report = subparsers.add_parser('report', help='Report a new issue.')
    parser_report.add_argument('-w', '--who', type=str, help='Whos doing it.', default=config.get('who'))
    parser_report.add_argument('WHAT', type=str, help='Whats happening.')
    parser_report.set_defaults(func=cmd_report)

    # list
    parser_report = subparsers.add_parser('list', help='List all open issues.')
    parser_report.set_defaults(func=cmd_list)

    # close
    parser_report = subparsers.add_parser('close', help='Close an open issue.')
    parser_report.add_argument('ID', type=int, help='ID to close.')
    parser_report.set_defaults(func=cmd_close)

    # steal
    parser_report = subparsers.add_parser('steal', help='Reassign an issue.')
    parser_report.add_argument('ID', type=int, help='ID to close.')
    parser_report.add_argument('-w', '--who', type=str, help='Tho whom.', default=config.get('who'))
    parser_report.set_defaults(func=cmd_steal)

    # parse
    args = arg_parser.parse_args()
    kernel = REST_Kernel(args.uri)

    # run subcommand
    args.func(args)
