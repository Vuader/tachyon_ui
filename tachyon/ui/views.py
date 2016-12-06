# Tachyon OSS Framework
#
# Copyright (c) 2016, see Authors.txt
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

import logging
from .restclient import RestClient

import nfw

log = logging.getLogger(__name__)

class Globals(nfw.Middleware):
    def __init__(self, app):
        self.config = app.config
        self.ui_config = app.config.get('ui')
        self.app_config = self.config.get('application')

    def pre(self, req, resp):
        req.context['url'] = self.ui_config.get('restapi','')
        nfw.jinja.globals['NAME'] = self.app_config.get('name')

class Menu():
    def __init__(self):
        self.items = []

    def add(self, item, link, view):
        self.items.append([item, link, view])

    def render(self, app):
        subs = {}
        menu = nfw.bootstrap3.Menu()
        for item in self.items:
            sub = menu
            item, link, view = item
            item = item.strip('/').split('/')
            for (i, l) in enumerate(item):
                if len(item)-1 == i:
                    sub.add_link(l,"%s/%s" % (app, link))
                else:
                    if l in subs:
                        sub = subs[l]
                    else:
                        s = nfw.bootstrap3.Menu()
                        subs[l] = s
                        if i == 0:
                            sub.add_dropdown(l,s)
                        else:
                            sub.add_submenu(l,s)
                        sub = s
        return menu

class Auth(nfw.Middleware):
    def __init__(self, app):
        pass

    def pre(self, req, resp):
        if req.session.get('token') is not None:
            nfw.jinja.globals['LOGIN'] = True
        nfw.jinja.globals['MENU'] = req.app_context['menu'].render(req.app)

class tachyon(nfw.Resource):
    def __init__(self, app):
        app.router.add(nfw.HTTP_GET, '/', self.home, 'UI:HOME')
        app.router.add(nfw.HTTP_GET, '/login', self.login, 'UI:LOGIN')
        app.router.add(nfw.HTTP_POST, '/login', self.login, 'UI:LOGIN')
        app.router.add(nfw.HTTP_GET, '/logout', self.logout, 'UI:LOGOUT')
        app.context['menu'] = Menu()
        #app.context['menu'].add('/main/login','/login','UI:LOGIN')
        #app.context['menu'].add('/main/testing/karoo','/logout','UI:LOGIN')

    def logout(self, req, resp):
        del req.session['token']
        if 'LOGIN' in nfw.jinja.globals:
            del nfw.jinja.globals['LOGIN']
        nfw.view('/login', nfw.HTTP_POST, req, resp)

    def home(self, req, resp):
        if req.session.get('token') is not None:
            t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
            resp.body = t.render()
        else:
            nfw.view('/login', nfw.HTTP_POST, req, resp)


    def login(self, req, resp):
        username = req.post.get('username','')
        password = req.post.get('password','')
        domain = req.post.get('domain','')
        url = req.context['url']
        error = []
        if username != '':
            api = RestClient(url)
            try:
                token = api.authenticate(username, password, domain)
                nfw.jinja.globals['LOGIN'] = True
                req.session['token'] = token
            except Exception as e:
                error.append(e)

        if req.session.get('token') is not None:
            nfw.view('/', nfw.HTTP_GET, req, resp)
        else:
            t = nfw.jinja.get_template('tachyon.ui/login.html')
            resp.body = t.render(username=username,password=password,domain=domain,error=error)

