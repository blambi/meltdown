#!/usr/bin/env python
import json
import urllib2

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

        if response.has_key('successful') and response['successful']:
            return True
        return False

# -- main
if __name__ == '__main__':
    kernel = REST_Kernel('http://localhost/meltdown/web/')

    print kernel.new_issue("Coder", "My sample issue!")
