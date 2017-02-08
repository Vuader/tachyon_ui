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

from tachyon.ui import RestClient

import nfw

log = logging.getLogger(__name__)


class Globals(nfw.Middleware):
    def __init__(self, app):
        self.config = app.config
        self.ui_config = app.config.get('ui')
        self.app_config = self.config.get('application')

    def pre(self, req, resp):
        req.context['url'] = self.ui_config.get('restapi', '')
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
                    sub.add_link(l, "%s/%s" % (app, link))
                else:
                    if l in subs:
                        sub = subs[l]
                    else:
                        s = nfw.bootstrap3.Menu()
                        subs[l] = s
                        if i == 0:
                            sub.add_dropdown(l, s)
                        else:
                            sub.add_submenu(l, s)
                        sub = s
        return menu


class Auth(nfw.Middleware):
    def __init__(self, app):
        pass

    def pre(self, req, resp):
        if req.session.get('token') is not None:
            nfw.jinja.globals['LOGIN'] = True
        nfw.jinja.globals['MENU'] = req.app_context['menu'].render(req.app)


class Customers(nfw.Resource):
    def __init__(self, app):
        app.router.add(nfw.HTTP_GET, '/customers', self.view, 'CUSTOMERS:VIEW')
        app.router.add(nfw.HTTP_GET, '/customers/view', self.view, 'CUSTOMERS:VIEW')
        app.router.add(nfw.HTTP_GET, '/customers/view/{customer_id}', self.view, 'CUSTOMERS:VIEW')
        app.router.add(nfw.HTTP_GET, '/customers/add', self.add, 'CUSTOMERS:ADMIN')
        app.router.add(nfw.HTTP_POST, '/customers/add', self.add, 'CUSTOMERS:ADMIN')
        app.router.add(nfw.HTTP_GET, '/customers/edit/{customer_id}', self.edit, 'CUSTOMERS:ADMIN')
        app.router.add(nfw.HTTP_POST, '/customers/edit/{customer_id}', self.edit, 'CUSTOMERS:ADMIN')

    def view(self, req, resp, customer_id=None):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()

    def add(self, req, resp):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()

    def edit(self, req, resp, customer_id):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()

class Service(nfw.Resource):
    def __init__(self, app):
        app.router.add(nfw.HTTP_GET, '/services', self.view, 'SERVICES:VIEW')
        app.router.add(nfw.HTTP_GET, '/services/view', self.view, 'SERVICES:VIEW')
        app.router.add(nfw.HTTP_GET, '/services/view/{customer_service_id}', self.view, 'SERVICES:VIEW')
        app.router.add(nfw.HTTP_GET, '/services/add', self.add, 'SERVICES:USER')
        app.router.add(nfw.HTTP_GET, '/services/add/{service_id}', self.add, 'SERVICES:USER')
        app.router.add(nfw.HTTP_GET, '/services/attend', self.attend, 'SERVICES:ADMIN')

    def view(self, req, resp, customer_service_id=None):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()

    def add(self, req, resp, service_id=None):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()

    def attend(self, req, resp):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()


class User(nfw.Resource):
    def __init__(self, app):
        app.router.add(nfw.HTTP_GET, '/users', self.view, 'USERS:VIEW')
        app.router.add(nfw.HTTP_GET, '/users/view', self.view, 'USERS:VIEW')
        app.router.add(nfw.HTTP_GET, '/users/view/{user_id}', self.view, 'USERS:VIEW')
        app.router.add(nfw.HTTP_GET, '/users/add', self.add, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_POST, '/users/add', self.add, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_GET, '/users/edit/{user_id}', self.edit, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_POST, '/users/edit/{user_id}', self.edit, 'USERS:ADMIN')

    def view(self, req, resp, user_id=None):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()

    def edit(self, req, resp, user_id=None):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()

    def add(self, req, resp):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()

class Roles(nfw.Resource):
    def __init__(self, app):
        app.router.add(nfw.HTTP_GET, '/users/roles', self.view, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_GET, '/users/roles/view', self.view, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_GET, '/users/roles/view/{role_id}', self.view, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_GET, '/users/roles/edit/{role_id}', self.edit, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_POST, '/users/roles/edit/{role_id}', self.edit, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_GET, '/users/roles/add', self.add, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_POST, '/users/roles/add', self.add, 'USERS:ADMIN')

    def view(self, req, resp, role_id=None):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()

    def edit(self, req, resp, role_id=None):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()

    def add(self, req, resp):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()

class Domains(nfw.Resource):
    def __init__(self, app):
        app.router.add(nfw.HTTP_GET, '/users/domains', self.view, 'USERS:VIEW')
        app.router.add(nfw.HTTP_GET, '/users/domains/view', self.view, 'USERS:VIEW')
        app.router.add(nfw.HTTP_GET, '/users/domains/view/{role_id}', self.view, 'USERS:VIEW')
        app.router.add(nfw.HTTP_GET, '/users/domains/edit/{role_id}', self.edit, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_POST, '/users/domains/edit/{role_id}', self.edit, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_GET, '/users/domains/add', self.add, 'USERS:ADMIN')
        app.router.add(nfw.HTTP_POST, '/users/domains/add', self.add, 'USERS:ADMIN')

    def view(self, req, resp, role_id=None):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()

    def edit(self, req, resp, role_id=None):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()

    def add(self, req, resp):
        t = nfw.jinja.get_template('tachyon.ui/dashboard.html')
        resp.body = t.render()

class Tachyon(nfw.Resource):
    def __init__(self, app):
        app.router.add(nfw.HTTP_GET, '/', self.home, 'TACHYON:PUBLIC')
        app.router.add(nfw.HTTP_GET, '/login', self.login, 'TACHYON:PUBLIC')
        app.router.add(nfw.HTTP_POST, '/login', self.login, 'TACHYON:PUBLIC')
        app.router.add(nfw.HTTP_GET, '/logout', self.logout, 'TACHYON:PUBLIC')
        app.context['menu'] = Menu()
        app.context['menu'].add('/Accounts/Customers','/customers','CUSTOMERS:VIEW')
        app.context['menu'].add('/Accounts/Users','/users','USERS:VIEW')
        app.context['menu'].add('/Accounts/Roles','/users/roles','USERS:VIEW')
        app.context['menu'].add('/Accounts/Domains','/users/domains','USERS:VIEW')

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

