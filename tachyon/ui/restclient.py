# Tachyon OSS Framework
#
# Copyright (c) 2016-2017, see Authors.txt
# All rights reserved.
#
# LICENSE: (BSD3-Clause)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENTSHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import thread
import json

try:
    # python 3
    from io import BytesIO
except ImportError:
    # python 2
    from StringIO import StringIO as BytesIO
try:
    # python 3
    from urllib.parse import urlencode
except ImportError:
    # python 2
    from urllib import urlencode

import nfw


log = logging.getLogger(__name__)

sessions = {}


class RestClient(nfw.RestClient):
    def __init__(self, url, username=None, password=None, domain=None):
        global sessions

        self.thread_id = thread.get_ident()
        if self.thread_id not in sessions:
            sessions[self.thread_id] = {}
        self.session = sessions[self.thread_id]

        self.url = url
        if url in self.session:
            self.username = self.session[url]['username']
            self.password = self.session[url]['password']
            self.domain = self.session[url]['domain']
            self.tachyon_headers = self.session[url]['headers']
            super(RestClient, self).__init__()
        else:
            self.session[url] = {}
            self.session[url]['username'] = username
            self.session[url]['password'] = password
            self.session[url]['domain'] = domain
            self.session[url]['headers'] = {}
            self.username = username
            self.password = password
            self.domain = domain
            super(RestClient, self).__init__()
            self.tachyon_headers = self.session[url]['headers']
            if username is not None:
                self.authenticate(url, username, password, domain)

    def authenticate(self, username, password, domain):
        url = self.url
        auth_url = "%s/login" % (url,)

        if 'token' in self.tachyon_headers:
            del self.tachyon_headers['token']

        self.tachyon_headers['X-Domain'] = domain

        data = {}
        data['username'] = username
        data['password'] = password
        data['expire'] = 1
        data = json.dumps(data)

        server_headers, body = self.execute("POST", auth_url,
                                            data, self.tachyon_headers)
        result = json.loads(body)

        if 'token' in result:
            self.token = result['token']
            self.tachyon_headers['X-Auth-Token'] = self.token
        else:
            raise nfw.Error("Could not connect/authenticate")

        self.session[url]['headers'] = self.tachyon_headers

        return self.token

    def domain(self, domain):
        self.tachyon_headers['X-Domain'] = domain
        self.session[url]['headers'] = self.tachyon_headers

    def tenant(self, tenant):
        self.tachyon_headers['X-Tenant'] = tenant
        self.session[url]['headers'] = self.tachyon_headers

    def execute(self, request, url, data=None, headers=None):
        if self.url not in url:
            url = "%s/%s" % (self.url, url)
        if headers is None:
            headers = self.tachyon_headers
        else:
            headers.update(self.tachyon_headers)

        return super(RestClient, self).execute(request, url, data, headers)
