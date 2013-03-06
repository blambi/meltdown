#!/usr/bin/env python
import json
import urllib2
import httplib2
import argparse

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

    def __put(self, body, uri = None):
        if body:
            raise BaseException, "Not implemented yet!"

        if uri:
            full_uri = self.base_uri + uri
        else:
            full_uri = self.base_uri

        http = httplib2.Http()
        response, content = http.request(full_uri, 'PUT', headers =
                                         {'User-Agent': self.user_agent})

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

# -- main
if __name__ == '__main__':
    # This needs some work, but basic arg parsing is ready
    arg_parse = argparse.ArgumentParser( description = "Meltdown client - Report whats up etc." )
    arg_parse.add_argument('-u', '--uri', type=str, help="URI to connect to (default http://localhost:80).", default="http://localhost:80")
    arg_parse.add_argument('-l', '--list', help="Lists open/closed/all issues.", nargs=1, metavar=('TYPE')) # Hmmm not sure how
    arg_parse.add_argument('-r', '--report', help="Report a new issue.", nargs=2, metavar=('WHO', 'WHAT'))
    arg_parse.add_argument('-c', '--close', help="Close an issue by id.", nargs=1, metavar=('ID',))
    args = arg_parse.parse_args()

    kernel = REST_Kernel(args.uri)

    if args.report:
        ret = kernel.new_issue(args.report[0], args.report[1])

        if ret and ret['error']:
            print("ERR: {0}.".format(ret['why']))
        elif ret:
            print("OK: Created issue #{0}.".format(ret['id']))
        else:
            print("ERR: Undefined error occurred.")

    elif args.close:
        ret = kernel.close_issue(args.close[0])

        if ret and ret['error']:
            print("ERR: {0}.".format(ret['why']))
        elif ret:
            print("OK: Closed issue #{0}.".format(ret['id']))
        else:
            print("ERR: Undefined error occurred.")

        pass
    elif args.list:
        pass
    else: # List all is the default..
        open_issues = kernel.get_all_open()

        print("ID\tWho\tWhat")
        for issue in open_issues:
            print("{0}\t{1}\t{2}".format(issue['id'],
                                         issue['who'],
                                         issue['what']))
