#!/usr/bin/env python
import json
import urllib2
import argparse

class REST_Kernel:
    def __init__(self, base_uri):
        self.base_uri = base_uri
        self.user_agent = "MeltdownPY 0.1"

    def __post(self, body, uri = None):
        body = json.dumps(body)

        if uri:
            full_uri = self.base_uri + uri
        else:
            full_uri = self.base_uri
        request = urllib2.Request(full_uri, body,
                                  {'Content-Type': 'application/json',
                                   'User-Agent': self.user_agent})
        fp = urllib2.urlopen((request))
        response = fp.read()
        return json.loads(response)

    def __put(self, body, uri = None):
        raise BaseException, "Not implemented yet!"

    def __get(self, body, uri = None):
        raise BaseException, "Not implemented yet!"

    def get_all_open(self):
        response = self.__get()
        return response

    def new_issue(self, who, what):
        """Tries to report a new issue to the server"""
        body = json.dumps({
                'who': who,
                'what': what})

        try:
            response = self.__post(body)
        except ValueError, why:
            return { 'error': True, 'message': why }

        if response.has_key('successful'):
            if response['successful']:
                return { 'error': False, 'id': response['id'] }
            else:
                return { 'error': True, 'message': response['why'] }
        return False

# -- main
if __name__ == '__main__':
    # This needs some work, but basic arg parsing is ready
    arg_parse = argparse.ArgumentParser( description = "Meltdown client - Report whats up etc." )
    arg_parse.add_argument('-u', '--uri', type=str, help="URI to connect to (default http://localhost:80).", default="http://localhost:80")
    arg_parse.add_argument('-l', '--list', help="Lists open/closed/all issues.", nargs=1, metavar=('TYPE')) # Hmmm not sure how
    arg_parse.add_argument('-r', '--report', help="Report a new issue.", nargs=2, metavar=('WHO', 'WHAT'))
    arg_parse.add_argument('-c', '--close', help="Close an issue by id.", nargs=1, metavar=('ID',))

    #arg_parse.add_argument('-a', '--action', type=str, help="Action to do: create, close, list, list_all. (default create)", default="create")
    #arg_parse.add_argument('who', type=str, help="Who is doing something", default='')
    #arg_parse.add_argument('what', type=str, help="What is happening", default='')
    #arg_parse.add_argument('id', type=int, help="Incident/Issue ID to close", default=-1)
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
        pass
    elif args.list:
        pass
    else: # List all is the default..
        print("Wohaha...")
